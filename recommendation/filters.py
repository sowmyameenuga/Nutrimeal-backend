"""
Diet-Aware Filtering Module.
Filters food items based on user dietary preferences and health goals
BEFORE feeding into the recommendation models.
"""
import pandas as pd


# Diet compatibility rules
DIET_COMPATIBILITY = {
    "Vegan": ["Vegan"],
    "Vegetarian": ["Vegan", "Vegetarian"],
    "Non-Vegetarian": ["Vegan", "Vegetarian", "Non-Vegetarian"],
}


def filter_by_diet(food_df: pd.DataFrame, user_diet: str) -> pd.DataFrame:
    """
    Filter foods based on user's dietary preference.

    Rules:
      - Vegan users      -> only Vegan foods
      - Vegetarian users  -> Vegan + Vegetarian foods
      - Non-Veg users     -> all foods

    Args:
        food_df: DataFrame with 'diet_type' column
        user_diet: one of 'Vegan', 'Vegetarian', 'Non-Vegetarian'

    Returns:
        Filtered DataFrame
    """
    allowed = DIET_COMPATIBILITY.get(user_diet, ["Vegan", "Vegetarian", "Non-Vegetarian"])
    return food_df[food_df["diet_type"].isin(allowed)].copy()


def filter_by_goal(food_df: pd.DataFrame, user_goal: str) -> pd.DataFrame:
    """
    Apply soft goal-based filtering — boost goal-matching foods
    but don't exclude others entirely.

    Returns DataFrame with an added 'goal_bonus' column.
    """
    df = food_df.copy()

    def compute_bonus(row):
        bonus = 0.0
        goal_tag = row.get("goal_tag", "All")

        # Direct match
        if goal_tag == user_goal or goal_tag == "All":
            bonus += 0.15

        # Calorie-based heuristics
        if user_goal == "Weight Loss":
            if row["calories"] <= 300:
                bonus += 0.10
            elif row["calories"] <= 400:
                bonus += 0.05
        elif user_goal == "Muscle Gain":
            if row["protein"] >= 25:
                bonus += 0.10
            elif row["protein"] >= 18:
                bonus += 0.05

        return bonus

    df["goal_bonus"] = df.apply(compute_bonus, axis=1)
    return df


def apply_filters(food_df: pd.DataFrame, user_diet: str,
                   user_goal: str) -> pd.DataFrame:
    """
    Apply all filters in sequence:
      1. Diet-based hard filter
      2. Goal-based soft bonus

    Returns filtered DataFrame with 'goal_bonus' column.
    """
    filtered = filter_by_diet(food_df, user_diet)
    filtered = filter_by_goal(filtered, user_goal)
    return filtered
