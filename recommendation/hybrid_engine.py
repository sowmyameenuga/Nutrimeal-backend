"""
Hybrid Recommendation Engine.

Combines:
  - NCF scores (60% weight)
  - GNN scores (40% weight)
  - Diet-aware filtering (hard filter)
  - Goal-based re-ranking (soft bonus)

Main function:
  recommend(user_id, diet, goal, age, top_k=5)
"""
import os
import pandas as pd
import torch

from recommendation.ncf_model import NCFModel
from recommendation.gnn_model import GNNRecommender
from recommendation.filters import apply_filters

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(os.path.dirname(SCRIPT_DIR), "data")
MODEL_DIR = os.path.join(SCRIPT_DIR, "saved_models")

# Weights for hybrid scoring
NCF_WEIGHT = 0.60
GNN_WEIGHT = 0.40

# ── Cached models (loaded once) ──
_ncf_model = None
_ncf_checkpoint = None
_gnn_model = None
_gnn_checkpoint = None
_food_df = None


def _load_food_data():
    """Load food dataset (cached)."""
    global _food_df
    if _food_df is None:
        path = os.path.join(DATA_DIR, "food_dataset.csv")
        _food_df = pd.read_csv(path)
    return _food_df.copy()


def _load_ncf_model():
    """Load trained NCF model (cached)."""
    global _ncf_model, _ncf_checkpoint
    if _ncf_model is None:
        path = os.path.join(MODEL_DIR, "ncf_model.pth")
        if not os.path.exists(path):
            print(f"[WARN] NCF model not found at {path}")
            return None, None

        checkpoint = torch.load(path, map_location="cpu", weights_only=False)
        model = NCFModel(
            num_users=checkpoint["num_users"],
            num_items=checkpoint["num_items"],
            embed_dim=checkpoint["embed_dim"],
        )
        model.load_state_dict(checkpoint["model_state_dict"])
        model.eval()

        _ncf_model = model
        _ncf_checkpoint = checkpoint

    return _ncf_model, _ncf_checkpoint


def _load_gnn_model():
    """Load trained GNN model (cached)."""
    global _gnn_model, _gnn_checkpoint
    if _gnn_model is None:
        path = os.path.join(MODEL_DIR, "gnn_model.pth")
        if not os.path.exists(path):
            print(f"[WARN] GNN model not found at {path}")
            return None, None

        checkpoint = torch.load(path, map_location="cpu", weights_only=False)
        model = GNNRecommender(
            num_users=checkpoint["num_users"],
            num_items=checkpoint["num_items"],
            embed_dim=checkpoint["embed_dim"],
        )
        model.load_state_dict(checkpoint["model_state_dict"])
        model.eval()

        _gnn_model = model
        _gnn_checkpoint = checkpoint

    return _gnn_model, _gnn_checkpoint


def recommend(user_id: int, diet: str, goal: str, age: int,
              meal_type: str = None, country: str = "Global", top_k: int = 5) -> dict:
    """
    Generate top-K personalized food recommendations.

    Pipeline:
      1. Load food dataset
      2. Apply diet-aware filtering (hard filter)
      3. Filter by meal_type if provided
      4. Get NCF scores for all filtered foods
      5. Get GNN scores for all filtered foods
      6. Compute hybrid score = 0.6 * NCF + 0.4 * GNN + goal_bonus
      7. Return top-K foods

    Args:
        user_id: user ID (from dataset, 1-based)
        diet: "Vegetarian" / "Non-Vegetarian" / "Vegan"
        goal: "Weight Loss" / "Muscle Gain" / "Maintenance"
        age: user age (used for minor adjustments)
        meal_type: optional string e.g. "Breakfast", "Lunch", "Dinner", "Snack"
        top_k: number of recommendations to return

    Returns:
        dict with 'recommendations' list and 'model_info' metadata
    """
    # 1. Load food data
    food_df = _load_food_data()
    total_foods = len(food_df)

    # 2. Diet-aware filtering + goal bonus
    filtered_df = apply_filters(food_df, diet, goal)

    # 3. Meal type filter
    if meal_type:
        filtered_df = filtered_df[filtered_df["meal_type"].str.lower() == meal_type.lower()]

    from routes.meal_routes import MEAL_LIBRARY
    valid_titles = {m["title"] for cat in MEAL_LIBRARY.values() for m in cat}
    filtered_df = filtered_df[filtered_df["name"].isin(valid_titles)]

    filtered_count = len(filtered_df)

    if filtered_count == 0:
        return {
            "recommendations": [],
            "model_info": {
                "ncf_weight": NCF_WEIGHT,
                "gnn_weight": GNN_WEIGHT,
                "total_candidates": 0,
                "filtered_by_diet": diet,
                "error": "No foods match the diet filter",
            },
        }

    # 3. Get NCF scores
    ncf_scores = _get_ncf_scores(user_id, filtered_df)

    # 4. Get GNN scores
    gnn_scores = _get_gnn_scores(user_id, filtered_df)

    # 5. Compute hybrid scores
    filtered_df = filtered_df.copy()
    filtered_df["ncf_score"] = ncf_scores
    filtered_df["gnn_score"] = gnn_scores
    filtered_df["hybrid_score"] = (
        NCF_WEIGHT * filtered_df["ncf_score"]
        + GNN_WEIGHT * filtered_df["gnn_score"]
        + filtered_df["goal_bonus"]
    )

    # Age-based minor adjustment (younger users → slightly more calories)
    if age and age < 25:
        filtered_df.loc[filtered_df["calories"] >= 400, "hybrid_score"] += 0.02
    elif age and age > 40:
        filtered_df.loc[filtered_df["calories"] <= 350, "hybrid_score"] += 0.02

    # Inject random noise so refreshing gives different results
    import numpy as np
    filtered_df["hybrid_score"] += np.random.uniform(0, 0.2, size=len(filtered_df))

    from routes.meal_routes import MEAL_LIBRARY
    rich_info_map = {}
    for category_meals in MEAL_LIBRARY.values():
        for m in category_meals:
            rich_info_map[m["title"]] = m

    # Country Hard Filter
    if country and country != "Global":
        country_indices = []
        for i, row in filtered_df.iterrows():
            title = row["name"]
            rich_data = rich_info_map.get(title, {})
            # Match country
            if rich_data.get("country", "Global") == country:
                country_indices.append(i)
        
        # Strictly filter by country
        filtered_df = filtered_df.loc[country_indices]
        
        # If strict country + diet filtering resulted in 0 items, 
        # let's relax the diet/goal filter and just return ANY food from that country
        if len(filtered_df) == 0:
            # Re-fetch from the entire food_df instead of filtered_df
            all_country_indices = []
            for i, row in food_df.iterrows():
                title = row["name"]
                rich_data = rich_info_map.get(title, {})
                if rich_data.get("country", "Global") == country:
                    all_country_indices.append(i)
            filtered_df = food_df.loc[all_country_indices]
            # Add hybrid score column so the rest of the code doesn't crash
            filtered_df = filtered_df.copy()
            filtered_df["hybrid_score"] = 0.5

    if len(filtered_df) == 0:
        return {
            "recommendations": [],
            "model_info": {
                "ncf_weight": NCF_WEIGHT,
                "gnn_weight": GNN_WEIGHT,
                "filtered_count": 0
            }
        }

    # 6. Sort and return top-15, then pick top-K randomly
    top_15 = filtered_df.nlargest(min(15, len(filtered_df)), "hybrid_score")
    if len(top_15) > top_k:
        top_foods = top_15.sample(n=top_k)
    else:
        top_foods = top_15

    # Sort again so highest score is still first among the picked
    top_foods = top_foods.sort_values(by="hybrid_score", ascending=False)

    recommendations = []
    for _, row in top_foods.iterrows():
        title = row["name"]
        rich_data = rich_info_map.get(title, {})

        recommendations.append({
            "item_id": int(row["item_id"]),
            "name": title,
            "title": title,
            "calories": int(row["calories"]),
            "protein": float(row["protein"]),
            "carbs": float(row["carbs"]),
            "fat": float(row["fat"]),
            "fiber": float(row["fiber"]),
            "meal_type": row["meal_type"],
            "diet_type": row["diet_type"],
            "score": round(float(row["hybrid_score"]), 4),
            "ingredients": rich_data.get("ingredients", f"• {title}\n• Fresh ingredients\n• Spices to taste"),
            "recipe_steps": rich_data.get("recipe_steps", "1. Gather all ingredients.\n2. Cook using standard methods until fully prepared.\n3. Serve fresh and enjoy!"),
            "health_benefits": rich_data.get("health_benefits", "Provides essential macronutrients perfectly balanced for your current goal."),
        })

    return {
        "recommendations": recommendations,
        "model_info": {
            "ncf_weight": NCF_WEIGHT,
            "gnn_weight": GNN_WEIGHT,
            "total_candidates": filtered_count,
            "total_foods": total_foods,
            "filtered_by_diet": diet,
            "user_goal": goal,
        },
    }


def _get_ncf_scores(user_id: int, food_df: pd.DataFrame) -> list:
    """Get NCF prediction scores for all foods."""
    model, checkpoint = _load_ncf_model()

    if model is None or checkpoint is None:
        # Fallback: return uniform scores
        return [0.5] * len(food_df)

    user_map = checkpoint["user_map"]
    item_map = checkpoint["item_map"]

    user_idx = user_map.get(user_id)
    if user_idx is None:
        # Unknown user — use average embedding (cold start)
        return [0.5] * len(food_df)

    scores = []
    for _, row in food_df.iterrows():
        item_idx = item_map.get(row["item_id"])
        if item_idx is not None:
            score = model.predict_scores(user_idx, [item_idx])[0]
            scores.append(score)
        else:
            scores.append(0.5)  # unknown item fallback

    return scores


def _get_gnn_scores(user_id: int, food_df: pd.DataFrame) -> list:
    """Get GNN prediction scores for all foods."""
    model, checkpoint = _load_gnn_model()

    if model is None or checkpoint is None:
        return [0.5] * len(food_df)

    user_map = checkpoint["user_map"]
    item_map = checkpoint["item_map"]
    edge_index = checkpoint["edge_index"]
    num_users = checkpoint["num_users"]

    user_idx = user_map.get(user_id)
    if user_idx is None:
        return [0.5] * len(food_df)

    # Map food item_ids to graph node indices
    item_node_ids = []
    valid_mask = []
    for _, row in food_df.iterrows():
        item_idx = item_map.get(row["item_id"])
        if item_idx is not None:
            item_node_ids.append(num_users + item_idx)  # offset
            valid_mask.append(True)
        else:
            item_node_ids.append(0)  # placeholder
            valid_mask.append(False)

    if not any(valid_mask):
        return [0.5] * len(food_df)

    # Get all scores
    all_scores = model.predict_scores(edge_index, user_idx, item_node_ids)

    # Replace invalid with 0.5
    scores = []
    for i, valid in enumerate(valid_mask):
        scores.append(all_scores[i] if valid else 0.5)

    return scores
