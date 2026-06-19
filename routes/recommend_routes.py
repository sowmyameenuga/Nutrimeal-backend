"""
Recommendation API Route.

POST /api/recommend — Get AI-powered personalized food recommendations.
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

recommend_bp = Blueprint("recommend", __name__, url_prefix="/api")


@recommend_bp.route("/recommend", methods=["POST"])
@jwt_required(optional=True)
def get_recommendations():
    """
    Get AI-powered food recommendations.

    Request body:
    {
        "user_id": 1,
        "diet": "Vegetarian",
        "goal": "Weight Loss",
        "age": 25,
        "top_k": 5  (optional, default=5)
    }

    Returns top-K food recommendations with hybrid scores.
    """
    data = request.get_json()

    if not data:
        return jsonify({"error": "Request body is required"}), 400

    user_id = data.get("user_id")
    diet = data.get("diet")
    goal = data.get("goal")
    age = data.get("age")
    top_k = data.get("top_k", 5)

    # Validation
    if user_id is None:
        return jsonify({"error": "user_id is required"}), 400
    # Lenient Mapping for Diet
    diet_map = {
        "Veg": "Vegetarian",
        "Vegetarian": "Vegetarian",
        "Non-Veg": "Non-Vegetarian",
        "Non-Vegetarian": "Non-Vegetarian",
        "Vegan": "Vegan"
    }
    diet = diet_map.get(diet, "Vegetarian")

    # Lenient Mapping for Goal
    goal_map = {
        "Weight Loss": "Weight Loss",
        "Fat Loss": "Weight Loss",
        "Muscle Gain": "Muscle Gain",
        "Weight Gain": "Muscle Gain",
        "Maintenance": "Maintenance",
        "Maintain Weight": "Maintenance"
    }
    goal = goal_map.get(goal, "Maintenance")
    meal_type = data.get("meal_type")
    country = data.get("country", "Global")

    try:
        from recommendation.hybrid_engine import recommend
        result = recommend(
            user_id=int(user_id),
            diet=diet,
            goal=goal,
            age=int(age) if age else 25,
            meal_type=meal_type,
            country=country,
            top_k=int(top_k),
        )
        return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": f"Recommendation failed: {str(e)}"}), 500
