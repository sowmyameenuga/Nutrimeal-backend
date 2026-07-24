from datetime import date
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import User, Profile, MealPlan, ProgressLog, LoggedMeal

dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/api/dashboard")


@dashboard_bp.route("", methods=["GET"])
@jwt_required()
def get_dashboard():
    """Return aggregated dashboard data in a single call."""
    user_id = int(get_jwt_identity())
    
    # Check for date query parameter
    date_str = request.args.get("date")
    if date_str:
        try:
            today = date.fromisoformat(date_str)
        except ValueError:
            today = date.today()
    else:
        today = date.today()

    user = User.query.get(user_id)
    profile = Profile.query.filter_by(user_id=user_id).first()
    progress = ProgressLog.query.filter_by(user_id=user_id, date=today).first()

    # Today's meals
    meals = MealPlan.query.filter_by(user_id=user_id, date=today).all()
    today_meals = {"breakfast": [], "lunch": [], "dinner": [], "snack": []}
    for m in meals:
        today_meals.setdefault(m.meal_type, []).append(m.to_dict())

    # Planned nutrition from today's meal plan
    planned_calories = sum(m.calories for m in meals)
    planned_protein = sum(m.protein for m in meals)
    planned_carbs = sum(m.carbs for m in meals)
    planned_fat = sum(m.fat for m in meals)

    # Actual consumed values calculated on-the-fly from LoggedMeal for specified date
    all_logged_today = LoggedMeal.query.filter_by(user_id=user_id, date=today).all()
    consumed_calories = sum(m.calories for m in all_logged_today)
    consumed_protein = sum(m.protein for m in all_logged_today)
    consumed_carbs = sum(m.carbs for m in all_logged_today)
    consumed_fat = sum(m.fat for m in all_logged_today)

    consumed_water = progress.water_litres if progress else 0.0
    water_glasses = int(consumed_water / 0.5) if consumed_water else 0  # 1 glass = 500ml

    return jsonify({
        "user_name": user.name if user else "User",
        "daily_summary": {
            "calories": consumed_calories,
            "planned_calories": planned_calories,
            "protein": round(consumed_protein, 1),
            "planned_protein": round(planned_protein, 1),
            "carbs": round(consumed_carbs, 1),
            "planned_carbs": round(planned_carbs, 1),
            "fat": round(consumed_fat, 1),
            "planned_fat": round(planned_fat, 1),
            "water": round(consumed_water, 1),
            "water_glasses": water_glasses,
        },
        "today_meals": today_meals,
        "profile_complete": profile is not None and profile.goal is not None,
    }), 200
