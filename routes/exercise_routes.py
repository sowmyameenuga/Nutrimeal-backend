from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, date, timedelta
from models import db, ExerciseLog, Profile

exercise_bp = Blueprint("exercise", __name__, url_prefix="/api/exercise")

# MET values mapping for exercise types and intensities
MET_MAP = {
    "Running": {"Low": 6.0, "Moderate": 8.3, "High": 11.8},
    "Walking": {"Low": 2.5, "Moderate": 3.5, "High": 4.5},
    "Cycling": {"Low": 4.0, "Moderate": 6.8, "High": 10.0},
    "Swimming": {"Low": 4.5, "Moderate": 6.0, "High": 8.0},
    "Weight Lifting": {"Low": 3.0, "Moderate": 5.0, "High": 6.0},
    "Weight Training": {"Low": 3.0, "Moderate": 5.0, "High": 6.0},
    "Jump Rope (Skipping)": {"Low": 7.0, "Moderate": 10.0, "High": 12.0},
    "Jump Rope": {"Low": 7.0, "Moderate": 10.0, "High": 12.0}
}

@exercise_bp.route("/recommend", methods=["GET"])
@jwt_required()
def recommend_exercise():
    """Recommend a personalized exercise based on the user's profile guidelines."""
    user_id = int(get_jwt_identity())
    profile = Profile.query.filter_by(user_id=user_id).first()

    if not profile or not profile.weight_kg or profile.weight_kg <= 0:
        return jsonify({
            "error": "Valid profile data (weight) must be set in your profile to receive recommendations."
        }), 400

    age = profile.age or 30
    weight = profile.weight_kg
    goal = profile.goal or "Maintain Weight"
    activity_level = getattr(profile, "activity_level", "Moderate") or "Moderate"

    # Rule-based exercise selection
    if weight > 95.0 or age > 55:
        # Low impact
        if goal in ["Weight Loss", "Fat Loss"]:
            exercise_name = "Swimming"
        else:
            exercise_name = "Walking"
    else:
        if goal in ["Muscle Gain", "Weight Gain"]:
            exercise_name = "Weight Lifting"
        elif goal in ["Weight Loss", "Fat Loss"]:
            if activity_level == "Active" and age < 40:
                exercise_name = "Jump Rope (Skipping)"
            else:
                exercise_name = "Running"
        else:
            exercise_name = "Cycling"

    # Determine intensity
    if activity_level == "Sedentary":
        intensity = "Low"
    elif activity_level in ["Light", "Moderate"]:
        intensity = "Moderate"
    else:
        intensity = "High"

    # Determine duration
    if activity_level == "Sedentary":
        duration = 15
    elif activity_level == "Light":
        duration = 20
    elif activity_level == "Moderate":
        duration = 30
    else:
        duration = 45

    # Age adjustments for intensity/duration
    if age > 50 and intensity == "High":
        intensity = "Moderate"
    if age > 65 and duration > 20:
        duration = 20

    # Calculate calories burned dynamically
    met = MET_MAP[exercise_name][intensity]
    duration_hours = duration / 60.0
    calories_burned = round(met * weight * duration_hours)

    if calories_burned <= 0:
        calories_burned = 1

    return jsonify({
        "exercise_name": exercise_name,
        "duration_minutes": duration,
        "intensity": intensity,
        "calories_burned": calories_burned
    }), 200

@exercise_bp.route("/log", methods=["POST"])
@jwt_required()
def log_exercise():
    """Log a new exercise record."""
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}

    exercise_name = data.get("exercise_name")
    duration = data.get("duration_minutes")
    intensity = data.get("intensity")
    date_str = data.get("date")

    # 1. Validation
    if not exercise_name or exercise_name not in MET_MAP:
        return jsonify({"error": "Please select a valid exercise type."}), 400

    try:
        duration = int(duration)
        if duration <= 0:
            raise ValueError
    except (TypeError, ValueError):
        return jsonify({"error": "Duration must be greater than 0 minutes."}), 400

    if not intensity or intensity not in ["Low", "Moderate", "High"]:
        return jsonify({"error": "Please select a valid intensity (Low, Moderate, High)."}), 400

    # Retrieve user profile and weight
    profile = Profile.query.filter_by(user_id=user_id).first()
    if not profile or not profile.weight_kg or profile.weight_kg <= 0:
        return jsonify({"error": "Valid user weight must be available in your profile before logging exercise."}), 400

    # Parse date (default to today)
    exercise_date = date.today()
    if date_str:
        try:
            exercise_date = date.fromisoformat(date_str)
        except ValueError:
            return jsonify({"error": "Invalid date format. Use YYYY-MM-DD."}), 400

    # 2. Dynamic Calorie Calculation
    met = MET_MAP[exercise_name][intensity]
    weight = profile.weight_kg
    duration_hours = duration / 60.0
    calories_burned = round(met * weight * duration_hours)

    if calories_burned <= 0:
        calories_burned = 1

    # 3. Save to database
    log = ExerciseLog(
        user_id=user_id,
        exercise_name=exercise_name,
        duration_minutes=duration,
        intensity=intensity,
        calories_burned=calories_burned,
        exercise_date=exercise_date
    )
    db.session.add(log)
    db.session.commit()

    return jsonify({
        "message": "Exercise logged successfully",
        "exercise": log.to_dict()
    }), 200

@exercise_bp.route("/today", methods=["GET"])
@jwt_required()
def get_today_exercises():
    """Get all exercise records logged today."""
    user_id = int(get_jwt_identity())
    today = date.today()

    logs = ExerciseLog.query.filter_by(user_id=user_id, exercise_date=today).all()
    total_burned = sum(log.calories_burned for log in logs)

    return jsonify({
        "date": today.isoformat(),
        "total_calories_burned": total_burned,
        "exercises": [log.to_dict() for log in logs]
    }), 200

@exercise_bp.route("/weekly", methods=["GET"])
@jwt_required()
def get_weekly_exercises():
    """Get daily exercise calorie totals for the current week (Sunday to Saturday)."""
    user_id = int(get_jwt_identity())
    today = date.today()

    # Get Sunday of current week
    idx = (today.weekday() + 1) % 7  # Mon=0 -> index 1, Sun=6 -> index 0
    week_start = today - timedelta(days=idx)
    week_end = week_start + timedelta(days=6)

    logs = ExerciseLog.query.filter(
        ExerciseLog.user_id == user_id,
        ExerciseLog.exercise_date >= week_start,
        ExerciseLog.exercise_date <= week_end
    ).all()

    # Map logs to specific weekdays
    daily_map = {week_start + timedelta(days=i): 0 for i in range(7)}
    for log in logs:
        if log.exercise_date in daily_map:
            daily_map[log.exercise_date] += log.calories_burned

    weekly_data = []
    days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
    for i, (d, cals) in enumerate(daily_map.items()):
        weekly_data.append({
            "date": d.isoformat(),
            "day_name": days[i],
            "calories_burned": cals
        })

    return jsonify({
        "week_start": week_start.isoformat(),
        "week_end": week_end.isoformat(),
        "data": weekly_data
    }), 200

@exercise_bp.route("/history", methods=["GET"])
@jwt_required()
def get_exercise_history():
    """Get exercise logs, optionally filtered by a specific date."""
    user_id = int(get_jwt_identity())
    date_str = request.args.get("date")

    if date_str:
        try:
            filter_date = date.fromisoformat(date_str)
            logs = ExerciseLog.query.filter_by(user_id=user_id, exercise_date=filter_date).all()
        except ValueError:
            return jsonify({"error": "Invalid date format. Use YYYY-MM-DD."}), 400
    else:
        logs = ExerciseLog.query.filter_by(user_id=user_id).order_by(ExerciseLog.exercise_date.desc(), ExerciseLog.created_at.desc()).all()

    return jsonify([log.to_dict() for log in logs]), 200
