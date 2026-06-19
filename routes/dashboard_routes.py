from datetime import date
from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import User, Profile, MealPlan, ProgressLog

dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/api/dashboard")


@dashboard_bp.route("", methods=["GET"])
@jwt_required()
def get_dashboard():
    """Return aggregated dashboard data in a single call."""
    user_id = int(get_jwt_identity())
    today = date.today()

    user = User.query.get(user_id)
    profile = Profile.query.filter_by(user_id=user_id).first()
    progress = ProgressLog.query.filter_by(user_id=user_id, date=today).first()

    # Today's meals
    meals = MealPlan.query.filter_by(user_id=user_id, date=today).all()
    today_meals = {"breakfast": [], "lunch": [], "dinner": [], "snack": []}
    for m in meals:
        today_meals.setdefault(m.meal_type, []).append({
            "id": m.id,
            "title": m.title,
            "calories": m.calories,
        })

    # Total nutrition from today's meal plan
    total_calories = sum(m.calories for m in meals)
    total_protein = sum(m.protein for m in meals)
    total_water = progress.water_litres if progress else 0.0

    return jsonify({
        "user_name": user.name if user else "User",
        "daily_summary": {
            "calories": total_calories,
            "protein": round(total_protein, 1),
            "water": round(total_water, 1),
        },
        "today_meals": today_meals,
        "profile_complete": profile is not None and profile.goal is not None,
    }), 200
