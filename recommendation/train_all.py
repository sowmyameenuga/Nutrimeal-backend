"""
Master Training Pipeline.

Runs the complete pipeline:
  1. Generate datasets (if not exists)
  2. Train NCF model
  3. Train GNN model

Run: python recommendation/train_all.py
"""
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SCRIPT_DIR)
DATA_DIR = os.path.join(ROOT_DIR, "data")

# Add paths
sys.path.insert(0, ROOT_DIR)


def main():
    print("=" * 60)
    print("  AI Nutrition Recommendation - Training Pipeline")
    print("=" * 60)

    # Step 1: Generate datasets if needed
    food_csv = os.path.join(DATA_DIR, "food_dataset.csv")
    if not os.path.exists(food_csv):
        print("\n[Step 1/3] Generating datasets...")
        sys.path.insert(0, ROOT_DIR)
        try:
            from expand_library import main as gen_main
            gen_main()
        except ImportError:
            print("expand_library module not found, skipping dataset generation.")
    else:
        print("\n[Step 1/3] Datasets already exist. Skipping generation.")

    # Step 2: Train NCF
    print("\n" + "=" * 60)
    print("[Step 2/3] Training NCF Model...")
    print("=" * 60)
    from recommendation.train_ncf import train as train_ncf
    train_ncf()

    # Step 3: Train GNN
    print("\n" + "=" * 60)
    print("[Step 3/3] Training GNN Model...")
    print("=" * 60)
    from recommendation.train_gnn import train as train_gnn
    train_gnn()

    # Summary
    model_dir = os.path.join(SCRIPT_DIR, "saved_models")
    print("\n" + "=" * 60)
    print("  Training Complete!")
    print("=" * 60)
    print(f"\n  Saved models:")
    for f in os.listdir(model_dir):
        fpath = os.path.join(model_dir, f)
        size_kb = os.path.getsize(fpath) / 1024
        print(f"    - {f} ({size_kb:.1f} KB)")

    print(f"\n  Ready! Start the server with: python run.py")
    print(f"  Then POST to /api/recommend to get AI recommendations.\n")


if __name__ == "__main__":
    main()
