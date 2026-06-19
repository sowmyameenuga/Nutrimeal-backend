"""
Graph Neural Network (GNN) Model for Recommendation.

Uses a simplified GraphSAGE-style architecture that works with
standard PyTorch (no torch_geometric dependency required for inference).

Architecture:
  - Bipartite graph: users + items as nodes, interactions as edges
  - 2-layer GraphSAGE convolution (mean aggregation)
  - Output: dot product of user and item embeddings -> score

For training, we use a custom message-passing implementation
to avoid hard dependency on torch_geometric at runtime.
"""
import torch
import torch.nn as nn
import torch.nn.functional as F


class SAGEConvLayer(nn.Module):
    """
    Single GraphSAGE convolution layer (mean aggregation).
    Implements: h_v = W * CONCAT(h_v, MEAN(h_u for u in N(v)))
    """

    def __init__(self, in_dim: int, out_dim: int):
        super(SAGEConvLayer, self).__init__()
        self.linear = nn.Linear(in_dim * 2, out_dim)

    def forward(self, x: torch.Tensor, edge_index: torch.Tensor) -> torch.Tensor:
        """
        Args:
            x: (num_nodes, in_dim) node features
            edge_index: (2, num_edges) edge list [source, target]

        Returns:
            (num_nodes, out_dim) updated node features
        """
        num_nodes = x.size(0)
        src, dst = edge_index[0], edge_index[1]

        # Aggregate: mean of neighbor features for each node
        agg = torch.zeros(num_nodes, x.size(1), device=x.device)
        count = torch.zeros(num_nodes, 1, device=x.device)

        agg.index_add_(0, dst, x[src])
        count.index_add_(0, dst, torch.ones(src.size(0), 1, device=x.device))
        count = count.clamp(min=1)  # avoid division by zero
        agg = agg / count

        # Concatenate self + aggregated neighbor features
        combined = torch.cat([x, agg], dim=1)
        out = self.linear(combined)

        return F.relu(out)


class GNNRecommender(nn.Module):
    """
    2-layer GraphSAGE model for user-item recommendation.

    Nodes: users (0..num_users-1) + items (num_users..num_users+num_items-1)
    Edges: user-item interactions (bidirectional)
    """

    def __init__(self, num_users: int, num_items: int, embed_dim: int = 64):
        super(GNNRecommender, self).__init__()

        self.num_users = num_users
        self.num_items = num_items
        self.num_nodes = num_users + num_items
        self.embed_dim = embed_dim

        # Initial node embeddings
        self.node_embedding = nn.Embedding(self.num_nodes, embed_dim)

        # GraphSAGE layers
        self.conv1 = SAGEConvLayer(embed_dim, embed_dim)
        self.conv2 = SAGEConvLayer(embed_dim, embed_dim)

        # Output projection
        self.out_proj = nn.Linear(embed_dim, embed_dim)

        self._init_weights()

    def _init_weights(self):
        nn.init.xavier_uniform_(self.node_embedding.weight)
        nn.init.xavier_uniform_(self.out_proj.weight)

    def forward(self, edge_index: torch.Tensor) -> torch.Tensor:
        """
        Forward pass: compute node embeddings via message passing.

        Args:
            edge_index: (2, num_edges) bidirectional edge list

        Returns:
            (num_nodes, embed_dim) node embeddings
        """
        x = self.node_embedding.weight

        # Layer 1
        x = self.conv1(x, edge_index)
        x = F.dropout(x, p=0.2, training=self.training)

        # Layer 2
        x = self.conv2(x, edge_index)

        # Project
        x = self.out_proj(x)

        return x

    def predict_scores(self, edge_index: torch.Tensor,
                       user_id: int, item_ids: list) -> list:
        """
        Predict recommendation scores for a user against multiple items.

        Args:
            edge_index: graph edges
            user_id: user node index (0-based)
            item_ids: list of item node indices (offset by num_users)

        Returns:
            list of float scores (sigmoid-normalized)
        """
        self.eval()
        with torch.no_grad():
            embeddings = self.forward(edge_index)

            user_emb = embeddings[user_id].unsqueeze(0)  # (1, embed_dim)
            item_embs = embeddings[item_ids]               # (K, embed_dim)

            # Dot product scores
            scores = torch.mm(user_emb, item_embs.t()).squeeze(0)  # (K,)
            scores = torch.sigmoid(scores)

            return scores.tolist()
