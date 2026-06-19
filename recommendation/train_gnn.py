"""
GNN Model Training Script.

Builds a bipartite user-item graph from interaction data,
trains a GraphSAGE model for link prediction, and saves weights.

Run: python recommendation/train_gnn.py
"""
import os
import sys
import numpy as np
import pandas as pd
import torch
import torch.nn as nn

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from recommendation.gnn_model import GNNRecommender

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(os.path.dirname(SCRIPT_DIR), "data")
MODEL_DIR = os.path.join(SCRIPT_DIR, "saved_models")


def build_graph(interactions_df, num_users, num_items, user_map, item_map):
    """
    Build bipartite graph edges from interactions.

    Node mapping:
      - Users: indices 0..num_users-1
      - Items: indices num_users..num_users+num_items-1

    Returns edge_index as (2, num_edges*2) tensor (bidirectional).
    """
    src_list = []
    dst_list = []

    for _, row in interactions_df.iterrows():
        uid = user_map.get(row["user_id"])
        iid = item_map.get(row["item_id"])

        if uid is None or iid is None:
            continue

        item_node = num_users + iid  # offset items

        # Bidirectional edges
        src_list.extend([uid, item_node])
        dst_list.extend([item_node, uid])

    edge_index = torch.tensor([src_list, dst_list], dtype=torch.long)
    return edge_index


def negative_sampling(edge_index, num_nodes, num_neg):
    """Generate random negative edges for training."""
    # Get existing edges as set
    existing = set()
    src, dst = edge_index[0].tolist(), edge_index[1].tolist()
    for s, d in zip(src, dst):
        existing.add((s, d))

    neg_src, neg_dst = [], []
    while len(neg_src) < num_neg:
        s = np.random.randint(0, num_nodes)
        d = np.random.randint(0, num_nodes)
        if s != d and (s, d) not in existing:
            neg_src.append(s)
            neg_dst.append(d)

    return torch.tensor([neg_src, neg_dst], dtype=torch.long)


def train():
    """Main GNN training loop."""
    print("\n========== GNN Training ==========\n")

    # Load data
    print("Loading data...")
    interactions = pd.read_csv(os.path.join(DATA_DIR, "interaction_dataset.csv"))
    foods = pd.read_csv(os.path.join(DATA_DIR, "food_dataset.csv"))

    unique_users = sorted(interactions["user_id"].unique())
    unique_items = sorted(interactions["item_id"].unique())

    user_map = {uid: idx for idx, uid in enumerate(unique_users)}
    item_map = {iid: idx for idx, iid in enumerate(unique_items)}

    num_users = len(unique_users)
    num_items = len(unique_items)
    num_nodes = num_users + num_items

    print(f"  Nodes: {num_nodes} (Users: {num_users}, Items: {num_items})")

    # Build graph
    edge_index = build_graph(interactions, num_users, num_items, user_map, item_map)
    print(f"  Edges: {edge_index.size(1)} (bidirectional)")

    # Initialize model
    model = GNNRecommender(num_users=num_users, num_items=num_items, embed_dim=64)
    optimizer = torch.optim.Adam(model.parameters(), lr=0.005)
    criterion = nn.BCEWithLogitsLoss()

    print(f"\n  Model parameters: {sum(p.numel() for p in model.parameters()):,}")

    # Training loop
    epochs = 50
    best_loss = float("inf")

    for epoch in range(1, epochs + 1):
        model.train()

        # Get node embeddings
        embeddings = model(edge_index)

        # Positive edges (sample subset for efficiency)
        num_pos = min(edge_index.size(1) // 2, 2000)
        perm = torch.randperm(edge_index.size(1) // 2)[:num_pos]
        pos_src = edge_index[0][perm * 2]
        pos_dst = edge_index[1][perm * 2]

        # Negative edges
        neg_edges = negative_sampling(edge_index, num_nodes, num_pos)
        neg_src = neg_edges[0]
        neg_dst = neg_edges[1]

        # Compute scores
        pos_scores = (embeddings[pos_src] * embeddings[pos_dst]).sum(dim=1)
        neg_scores = (embeddings[neg_src] * embeddings[neg_dst]).sum(dim=1)

        # Labels
        pos_labels = torch.ones(num_pos)
        neg_labels = torch.zeros(num_pos)

        # Loss
        scores = torch.cat([pos_scores, neg_scores])
        labels = torch.cat([pos_labels, neg_labels])

        loss = criterion(scores, labels)

        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        if epoch % 10 == 0 or epoch == 1:
            # Compute AUC-like metric
            with torch.no_grad():
                pos_mean = torch.sigmoid(pos_scores).mean().item()
                neg_mean = torch.sigmoid(neg_scores).mean().item()
            print(f"  Epoch {epoch:3d}/{epochs} | Loss: {loss.item():.4f} | "
                  f"Pos: {pos_mean:.3f} | Neg: {neg_mean:.3f}")

        if loss.item() < best_loss:
            best_loss = loss.item()

    # Final evaluation
    print("\n--- Final Evaluation ---")
    model.eval()
    with torch.no_grad():
        embeddings = model(edge_index)

        # Test on some positive edges
        test_pos = min(500, edge_index.size(1) // 2)
        perm = torch.randperm(edge_index.size(1) // 2)[:test_pos]
        pos_src = edge_index[0][perm * 2]
        pos_dst = edge_index[1][perm * 2]
        pos_scores = torch.sigmoid(
            (embeddings[pos_src] * embeddings[pos_dst]).sum(dim=1)
        )

        # Test on negative edges
        neg_edges = negative_sampling(edge_index, num_nodes, test_pos)
        neg_scores = torch.sigmoid(
            (embeddings[neg_edges[0]] * embeddings[neg_edges[1]]).sum(dim=1)
        )

        # Accuracy
        pos_correct = (pos_scores > 0.5).float().mean().item()
        neg_correct = (neg_scores < 0.5).float().mean().item()
        accuracy = (pos_correct + neg_correct) / 2

        print(f"  Positive score mean: {pos_scores.mean().item():.4f}")
        print(f"  Negative score mean: {neg_scores.mean().item():.4f}")
        print(f"  Link prediction accuracy: {accuracy:.4f}")
        print(f"  Best training loss: {best_loss:.4f}")

    # Save model
    os.makedirs(MODEL_DIR, exist_ok=True)
    model_path = os.path.join(MODEL_DIR, "gnn_model.pth")
    torch.save({
        "model_state_dict": model.state_dict(),
        "num_users": num_users,
        "num_items": num_items,
        "embed_dim": 64,
        "user_map": user_map,
        "item_map": item_map,
        "edge_index": edge_index,
    }, model_path)
    print(f"\n  Model saved to: {model_path}")

    return model


if __name__ == "__main__":
    train()
