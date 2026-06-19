from datetime import date, timedelta
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, ProgressLog, Profile

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
    water_target = 3.0
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
    """Add a meal's calories to today's progress."""
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}
    calories = data.get("calories", 0)
    
    today = date.today()
    log = ProgressLog.query.filter_by(user_id=user_id, date=today).first()
    
    if log is None:
        log = ProgressLog(user_id=user_id, date=today)
        db.session.add(log)
        
    log.calories_consumed += int(calories)
    db.session.commit()
    
    return jsonify({
        "message": f"Added {calories} kcal successfully",
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
