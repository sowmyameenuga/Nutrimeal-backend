from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, User, Profile

profile_bp = Blueprint("profile", __name__, url_prefix="/api/profile")


@profile_bp.route("", methods=["GET"])
@jwt_required()
def get_profile():
    """Return the current user's profile."""
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)

    if user is None:
        return jsonify({"error": "User not found"}), 404

    profile = Profile.query.filter_by(user_id=user_id).first()

    if profile is None:
        # Return empty profile with user name
        return jsonify({
            "user_id": user_id,
            "name": user.name,
            "age": None,
            "gender": None,
            "height_cm": None,
            "weight_kg": None,
            "goal": None,
            "allergy": None,
        }), 200

    return jsonify(profile.to_dict()), 200


@profile_bp.route("", methods=["POST"])
@jwt_required()
def save_profile():
    """Create or update the current user's profile."""
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}

    user = User.query.get(user_id)
    if user is None:
        return jsonify({"error": "User not found"}), 404

    # Update user name if provided
    if "name" in data and data["name"].strip():
        user.name = data["name"].strip()

    profile = Profile.query.filter_by(user_id=user_id).first()

    if profile is None:
        profile = Profile(user_id=user_id)
        db.session.add(profile)

    # Update profile fields
    if "age" in data:
        profile.age = int(data["age"]) if data["age"] else None
    if "gender" in data:
        profile.gender = data["gender"]
    if "height_cm" in data:
        profile.height_cm = float(data["height_cm"]) if data["height_cm"] else None
    if "weight_kg" in data:
        profile.weight_kg = float(data["weight_kg"]) if data["weight_kg"] else None
    if "goal" in data:
        profile.goal = data["goal"]
    if "allergy" in data:
        profile.allergy = data["allergy"]
    if "diet" in data:
        profile.diet = data["diet"]
    if "country" in data:
        profile.country = data["country"]

    db.session.commit()

    return jsonify({
        "message": "Profile saved successfully",
        "profile": profile.to_dict(),
    }), 200
