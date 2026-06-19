"""
NCF Model Training Script.

Loads interaction data, trains the NCF model, evaluates performance,
and saves the trained model weights.

Run: python recommendation/train_ncf.py
"""
import os
import sys
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from sklearn.model_selection import train_test_split

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from recommendation.ncf_model import NCFModel

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(os.path.dirname(SCRIPT_DIR), "data")
MODEL_DIR = os.path.join(SCRIPT_DIR, "saved_models")


class InteractionDataset(Dataset):
    """PyTorch Dataset for user-item interactions."""

    def __init__(self, user_ids, item_ids, labels):
        self.user_ids = torch.tensor(user_ids, dtype=torch.long)
        self.item_ids = torch.tensor(item_ids, dtype=torch.long)
        self.labels = torch.tensor(labels, dtype=torch.float32)

    def __len__(self):
        return len(self.labels)

    def __getitem__(self, idx):
        return self.user_ids[idx], self.item_ids[idx], self.labels[idx]


def load_data():
    """Load and prepare interaction data."""
    interactions = pd.read_csv(os.path.join(DATA_DIR, "interaction_dataset.csv"))
    foods = pd.read_csv(os.path.join(DATA_DIR, "food_dataset.csv"))

    # Create 0-based index mappings
    unique_users = sorted(interactions["user_id"].unique())
    unique_items = sorted(interactions["item_id"].unique())

    user_to_idx = {uid: idx for idx, uid in enumerate(unique_users)}
    item_to_idx = {iid: idx for idx, iid in enumerate(unique_items)}

    # Map to indices
    user_ids = interactions["user_id"].map(user_to_idx).values
    item_ids = interactions["item_id"].map(item_to_idx).values
    labels = interactions["liked"].values.astype(np.float32)

    num_users = len(unique_users)
    num_items = len(unique_items)

    print(f"  Users: {num_users}, Items: {num_items}, Interactions: {len(labels)}")
    print(f"  Positive ratio: {labels.mean():.3f}")

    return user_ids, item_ids, labels, num_users, num_items, user_to_idx, item_to_idx


def precision_at_k(model, test_users, test_items, test_labels, k=5):
    """Compute Precision@K on test set."""
    model.eval()
    precisions = []

    unique_users = np.unique(test_users)
    for uid in unique_users[:50]:  # evaluate on subset for speed
        mask = test_users == uid
        if mask.sum() < k:
            continue

        items = test_items[mask]
        labels = test_labels[mask]

        with torch.no_grad():
            scores = model.predict_scores(uid, items.tolist())

        top_k_indices = np.argsort(scores)[-k:]
        precision = labels[top_k_indices].mean()
        precisions.append(precision)

    return np.mean(precisions) if precisions else 0.0


def train():
    """Main training loop."""
    print("\n========== NCF Training ==========\n")

    # Load data
    print("Loading data...")
    user_ids, item_ids, labels, num_users, num_items, user_map, item_map = load_data()

    # Train/test split
    (train_users, test_users, train_items, test_items,
     train_labels, test_labels) = train_test_split(
        user_ids, item_ids, labels, test_size=0.2, random_state=42
    )

    # Create dataset & dataloader
    train_dataset = InteractionDataset(train_users, train_items, train_labels)
    train_loader = DataLoader(train_dataset, batch_size=64, shuffle=True)

    # Initialize model
    model = NCFModel(num_users=num_users, num_items=num_items, embed_dim=32)
    criterion = nn.BCELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

    print(f"\nModel parameters: {sum(p.numel() for p in model.parameters()):,}")
    print(f"Training samples: {len(train_users)}")
    print(f"Test samples: {len(test_users)}\n")

    # Training loop
    epochs = 50
    best_loss = float("inf")

    for epoch in range(1, epochs + 1):
        model.train()
        total_loss = 0
        n_batches = 0

        for batch_users, batch_items, batch_labels in train_loader:
            optimizer.zero_grad()
            predictions = model(batch_users, batch_items)
            loss = criterion(predictions, batch_labels)
            loss.backward()
            optimizer.step()

            total_loss += loss.item()
            n_batches += 1

        avg_loss = total_loss / n_batches

        if epoch % 10 == 0 or epoch == 1:
            p_at_5 = precision_at_k(model, test_users, test_items, test_labels, k=5)
            print(f"  Epoch {epoch:3d}/{epochs} | Loss: {avg_loss:.4f} | P@5: {p_at_5:.4f}")

        if avg_loss < best_loss:
            best_loss = avg_loss

    # Final evaluation
    print("\n--- Final Evaluation ---")
    p_at_5 = precision_at_k(model, test_users, test_items, test_labels, k=5)
    p_at_10 = precision_at_k(model, test_users, test_items, test_labels, k=10)
    print(f"  Precision@5:  {p_at_5:.4f}")
    print(f"  Precision@10: {p_at_10:.4f}")
    print(f"  Best Loss:    {best_loss:.4f}")

    # Save model
    os.makedirs(MODEL_DIR, exist_ok=True)
    model_path = os.path.join(MODEL_DIR, "ncf_model.pth")
    torch.save({
        "model_state_dict": model.state_dict(),
        "num_users": num_users,
        "num_items": num_items,
        "embed_dim": 32,
        "user_map": user_map,
        "item_map": item_map,
    }, model_path)
    print(f"\n  Model saved to: {model_path}")

    return model


if __name__ == "__main__":
    train()
