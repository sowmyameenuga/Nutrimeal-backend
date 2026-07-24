from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from models import db, User

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.route("/signup", methods=["POST"])
def signup():
    """Register a new user and return a JWT token."""
    data = request.get_json() or {}

    # ── Validation ──
    name = data.get("name", "").strip()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not name or not email or not password:
        return jsonify({"error": "Name, email and password are required"}), 400

    if len(password) < 4:
        return jsonify({"error": "Password must be at least 4 characters"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already registered"}), 409

    # ── Create user ──
    user = User(name=name, email=email)
    user.set_password(password)

    db.session.add(user)
    db.session.commit()

    token = create_access_token(identity=str(user.id))

    return jsonify({
        "message": "Account created successfully",
        "token": token,
        "user": user.to_dict(),
    }), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    """Authenticate user and return a JWT token."""
    data = request.get_json() or {}

    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    user = User.query.filter_by(email=email).first()

    if user is None or not user.check_password(password):
        return jsonify({"error": "Invalid email or password"}), 401

    token = create_access_token(identity=str(user.id))

    return jsonify({
        "message": "Login successful",
        "token": token,
        "user": user.to_dict(),
    }), 200


@auth_bp.route("/logout", methods=["POST"])
def logout():
    """Logout (client should discard token)."""
    return jsonify({"message": "Logged out successfully"}), 200


@auth_bp.route("/forgot-password", methods=["POST"])
def forgot_password():
    """Send a password-reset token for the given email.
    Since we don't have email infra, we return the token directly
    so the client can immediately show the reset form.
    """
    data = request.get_json() or {}
    email = data.get("email", "").strip().lower()

    if not email:
        return jsonify({"error": "Email is required"}), 400

    user = User.query.filter_by(email=email).first()

    if user is None:
        return jsonify({"error": "No account found with this email"}), 404

    # Generate a short-lived token for password reset
    reset_token = create_access_token(
        identity=str(user.id),
        additional_claims={"purpose": "password_reset"},
    )

    return jsonify({
        "message": "Reset token generated",
        "reset_token": reset_token,
    }), 200


@auth_bp.route("/reset-password", methods=["POST"])
def reset_password():
    """Reset password using a valid reset token."""
    data = request.get_json() or {}

    reset_token = data.get("reset_token", "")
    new_password = data.get("new_password", "")

    if not reset_token or not new_password:
        return jsonify({"error": "Token and new password are required"}), 400

    if len(new_password) < 4:
        return jsonify({"error": "Password must be at least 4 characters"}), 400

    # Decode the token to get user id
    from flask_jwt_extended import decode_token
    try:
        decoded = decode_token(reset_token)
        user_id = decoded["sub"]
        purpose = decoded.get("purpose", "")
        if purpose != "password_reset":
            return jsonify({"error": "Invalid reset token"}), 400
    except Exception:
        return jsonify({"error": "Invalid or expired reset token"}), 400

    user = User.query.get(int(user_id))
    if user is None:
        return jsonify({"error": "User not found"}), 404

    user.set_password(new_password)
    db.session.commit()

    return jsonify({"message": "Password reset successfully"}), 200


@auth_bp.route("/change-password", methods=["PUT"])
@jwt_required()
def change_password():
    """Change password for an authenticated user."""
    user_id = int(get_jwt_identity())

    data = request.get_json() or {}
    old_password = data.get("old_password", "")
    new_password = data.get("new_password", "")

    if not old_password or not new_password:
        return jsonify({"error": "Both old and new passwords are required"}), 400

    if len(new_password) < 4:
        return jsonify({"error": "New password must be at least 4 characters"}), 400

    user = User.query.get(user_id)
    if user is None:
        return jsonify({"error": "User not found"}), 404

    if not user.check_password(old_password):
        return jsonify({"error": "Incorrect current password"}), 401

    user.set_password(new_password)
    db.session.commit()

    return jsonify({"message": "Password changed successfully"}), 200


@auth_bp.route("/account", methods=["DELETE"])
@jwt_required()
def delete_account():
    """Permanently delete the authenticated user's account and all data."""
    user_id = int(get_jwt_identity())

    user = User.query.get(user_id)
    if user is None:
        return jsonify({"error": "User not found"}), 404

    db.session.delete(user)
    db.session.commit()

    return jsonify({"message": "Account deleted successfully"}), 200
