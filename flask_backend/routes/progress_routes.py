from datetime import date, timedelta
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, ProgressLog, Profile, LoggedMeal, MealPlan

progress_bp = Blueprint("progress", __name__, url_prefix="/api/progress")


@progress_bp.route("/daily", methods=["GET"])
@jwt_required()
def get_daily_progress():
    """Return today's progress for the current user."""
    user_id = int(get_jwt_identity())
    today = date.today()

    log = ProgressLog.query.filter_by(user_id=user_id, date=today).first()
    profile = Profile.query.filter_by(user_id=user_id).first()

    # Target values based on profile
    calorie_target = 2000
    water_target = 4.0
    weight_goal = 60.0

    if profile:
        # Simple calorie target estimation based on goal
        if profile.goal == "Weight Loss" or profile.goal == "Fat Loss":
            calorie_target = 1600
        elif profile.goal == "Weight Gain" or profile.goal == "Muscle Gain":
            calorie_target = 2500
        else:
            calorie_target = 2000

        if profile.weight_kg:
            if profile.goal == "Weight Loss" or profile.goal == "Fat Loss":
                weight_goal = profile.weight_kg - 5
            elif profile.goal == "Weight Gain" or profile.goal == "Muscle Gain":
                weight_goal = profile.weight_kg + 5
            else:
                weight_goal = profile.weight_kg

    result = {
        "date": today.isoformat(),
        "calories_consumed": log.calories_consumed if log else 0,
        "calorie_target": calorie_target,
        "water_litres": log.water_litres if log else 0.0,
        "water_target": water_target,
        "current_weight": log.current_weight if log else (profile.weight_kg if profile else 0),
        "weight_goal": weight_goal,
    }

    return jsonify(result), 200


@progress_bp.route("/log", methods=["POST"])
@jwt_required()
def log_progress():
    """Log or update today's progress entry."""
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}
    today = date.today()

    log = ProgressLog.query.filter_by(user_id=user_id, date=today).first()

    if log is None:
        log = ProgressLog(user_id=user_id, date=today)
        db.session.add(log)

    if "calories_consumed" in data:
        log.calories_consumed = int(data["calories_consumed"])
    if "protein_consumed" in data:
        log.protein_consumed = float(data["protein_consumed"])
    if "water_litres" in data:
        log.water_litres = float(data["water_litres"])
    if "current_weight" in data:
        log.current_weight = float(data["current_weight"])

    db.session.commit()

    return jsonify({
        "message": "Progress logged successfully",
        "progress": log.to_dict(),
    }), 200


@progress_bp.route("/log_meal", methods=["POST"])
@jwt_required()
def log_meal():
    """Add a meal to today's logged meals and update progress."""
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}
    
    meal_id = data.get("meal_id")
    title = data.get("title", "Unknown Meal")
    calories = int(data.get("calories", 0))
    protein = float(data.get("protein", 0))
    carbs = float(data.get("carbs", 0))
    fat = float(data.get("fat", 0))
    confirm_duplicate = data.get("confirm_duplicate", False)

    date_str = data.get("date")
    if date_str:
        try:
            today = date.fromisoformat(date_str)
        except ValueError:
            today = date.today()
    else:
        today = date.today()

    # Check for duplicate if not confirmed
    if not confirm_duplicate:
        existing = LoggedMeal.query.filter_by(user_id=user_id, date=today, title=title).first()
        if existing:
            return jsonify({
                "error": "Duplicate meal",
                "message": f"You already logged '{title}' today."
            }), 409

    completion_time = data.get("completion_time")
    if not completion_time:
        from datetime import datetime, timezone, timedelta
        completion_time = datetime.now(timezone.utc).astimezone(timezone(timedelta(hours=5, minutes=30))).strftime('%I:%M %p')

    # Add the logged meal
    logged_meal = LoggedMeal(
        user_id=user_id,
        meal_id=meal_id,
        title=title,
        calories=calories,
        protein=protein,
        carbs=carbs,
        fat=fat,
        date=today,
        completion_time=completion_time
    )
    db.session.add(logged_meal)

    # Mark corresponding MealPlan as eaten
    if meal_id:
        meal = MealPlan.query.filter_by(id=meal_id, user_id=user_id).first()
        if meal:
            meal.eaten = True
            meal.completion_time = completion_time

    db.session.commit()

    # Recalculate daily totals from all logged meals today
    all_logged_today = LoggedMeal.query.filter_by(user_id=user_id, date=today).all()
    total_calories = sum(m.calories for m in all_logged_today)
    total_protein = sum(m.protein for m in all_logged_today)

    # Update ProgressLog
    log = ProgressLog.query.filter_by(user_id=user_id, date=today).first()
    if log is None:
        log = ProgressLog(user_id=user_id, date=today)
        db.session.add(log)
    
    log.calories_consumed = total_calories
    log.protein_consumed = total_protein
    db.session.commit()

    return jsonify({
        "message": "Meal logged successfully",
        "progress": log.to_dict(),
    }), 200


@progress_bp.route("/weekly", methods=["GET"])
@jwt_required()
def get_weekly_activity():
    """Return the last 7 days of activity."""
    user_id = int(get_jwt_identity())
    today = date.today()
    week_start = today - timedelta(days=6)

    logs = (
        ProgressLog.query
        .filter(
            ProgressLog.user_id == user_id,
            ProgressLog.date >= week_start,
            ProgressLog.date <= today,
        )
        .order_by(ProgressLog.date.asc())
        .all()
    )

    log_map = {log.date: log for log in logs}

    week_data = []
    for i in range(7):
        d = week_start + timedelta(days=i)
        log = log_map.get(d)
        week_data.append({
            "date": d.isoformat(),
            "day_name": d.strftime("%A"),
            "calories_consumed": log.calories_consumed if log else 0,
            "water_litres": log.water_litres if log else 0.0,
            "current_weight": log.current_weight if log else 0,
        })

    return jsonify(week_data), 200
