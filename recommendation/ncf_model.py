"""
Neural Collaborative Filtering (NCF) Model.

Architecture:
  User ID -> Embedding(num_users, 32) --+
                                         |--> Concat --> MLP(64->32->16->1) --> Sigmoid
  Item ID -> Embedding(num_items, 32) --+

Loss: Binary Cross Entropy
Predicts: P(user likes item)
"""
import torch
import torch.nn as nn


class NCFModel(nn.Module):
    """Neural Collaborative Filtering with MLP layers."""

    def __init__(self, num_users: int, num_items: int, embed_dim: int = 32):
        super(NCFModel, self).__init__()

        self.num_users = num_users
        self.num_items = num_items
        self.embed_dim = embed_dim

        # Embedding layers
        self.user_embedding = nn.Embedding(num_users, embed_dim)
        self.item_embedding = nn.Embedding(num_items, embed_dim)

        # MLP layers
        self.mlp = nn.Sequential(
            nn.Linear(embed_dim * 2, 64),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(32, 16),
            nn.ReLU(),
            nn.Linear(16, 1),
            nn.Sigmoid(),
        )

        # Initialize weights
        self._init_weights()

    def _init_weights(self):
        nn.init.xavier_uniform_(self.user_embedding.weight)
        nn.init.xavier_uniform_(self.item_embedding.weight)
        for layer in self.mlp:
            if isinstance(layer, nn.Linear):
                nn.init.xavier_uniform_(layer.weight)
                nn.init.zeros_(layer.bias)

    def forward(self, user_ids: torch.Tensor, item_ids: torch.Tensor) -> torch.Tensor:
        """
        Forward pass.

        Args:
            user_ids: (batch_size,) tensor of user indices
            item_ids: (batch_size,) tensor of item indices

        Returns:
            (batch_size, 1) tensor of predicted probabilities
        """
        user_emb = self.user_embedding(user_ids)   # (B, embed_dim)
        item_emb = self.item_embedding(item_ids)   # (B, embed_dim)

        concat = torch.cat([user_emb, item_emb], dim=1)  # (B, embed_dim*2)
        output = self.mlp(concat)  # (B, 1)

        return output.squeeze(-1)  # (B,)

    def predict_scores(self, user_id: int, item_ids: list) -> list:
        """
        Predict scores for a single user against multiple items.

        Args:
            user_id: single user index
            item_ids: list of item indices

        Returns:
            list of float scores
        """
        self.eval()
        with torch.no_grad():
            user_tensor = torch.tensor([user_id] * len(item_ids), dtype=torch.long)
            item_tensor = torch.tensor(item_ids, dtype=torch.long)
            scores = self.forward(user_tensor, item_tensor)
            return scores.tolist()
