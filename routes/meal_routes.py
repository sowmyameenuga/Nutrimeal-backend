import random
from datetime import date
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, User, Profile, MealPlan

meal_bp = Blueprint("meals", __name__, url_prefix="/api/meals")

# ═══════════════════════════════════════════════════════════════════════════════
#  EXPANDED MEAL LIBRARY — 60+ items with full nutrition, recipes, and diet tags
# ═══════════════════════════════════════════════════════════════════════════════

import json
import os

_lib_path = os.path.join(os.path.dirname(__file__), '..', 'meal_library_data.json')
with open(_lib_path, 'r', encoding='utf-8') as _f:
    MEAL_LIBRARY = json.load(_f)

def _filter_meals(pool, allergy, diet):
    # Basic filtering just for the daily generated plan
    res = []
    for m in pool:
        if diet == "Vegan" and m.get("diet_type") != "Vegan": continue
        if diet == "Vegetarian" and m.get("diet_type") == "Non-Vegetarian": continue
        if allergy and allergy != "None" and allergy.lower() in m.get("ingredients", "").lower(): continue
        res.append(m)
    return res

def _pick_meals(pool, count):
    if not pool: return []
    if len(pool) <= count: return pool
    return random.sample(pool, count)

def generate_meal_plan(user_id: int, profile):
    """Generate a day's meal plan based on user profile — respects diet + allergy."""
    allergy = profile.allergy if profile else "None"
    diet = profile.diet if profile else "Veg"
    today = date.today()

    # Remove old plans for today
    MealPlan.query.filter_by(user_id=user_id, date=today).delete()

    meal_counts = {"breakfast": 2, "lunch": 3, "dinner": 3, "snack": 3}

    for meal_type, count in meal_counts.items():
        pool = MEAL_LIBRARY.get(meal_type, [])
        filtered = _filter_meals(pool, allergy, diet)
        chosen = _pick_meals(filtered, count)

        for m in chosen:
            plan = MealPlan(
                user_id=user_id,
                meal_type=meal_type,
                title=m["title"],
                calories=m["calories"],
                protein=m["protein"],
                carbs=m["carbs"],
                fat=m["fat"],
                ingredients=m["ingredients"],
                health_benefits=m["health_benefits"],
                recipe_steps=m["recipe_steps"],
                date=today,
            )
            db.session.add(plan)

    db.session.commit()


# ─── Routes ──────────────────────────────────────────────────────────────────

@meal_bp.route("", methods=["GET"])
@jwt_required()
def get_meals():
    """Return today's meal plan grouped by type."""
    user_id = int(get_jwt_identity())
    today = date.today()

    meals = MealPlan.query.filter_by(user_id=user_id, date=today).all()

    grouped = {"breakfast": [], "lunch": [], "dinner": [], "snack": []}
    for m in meals:
        grouped.setdefault(m.meal_type, []).append(m.to_dict())

    return jsonify(grouped), 200


@meal_bp.route("/<int:meal_id>", methods=["GET"])
@jwt_required()
def get_meal_detail(meal_id):
    """Return full details for a single meal."""
    user_id = int(get_jwt_identity())
    meal = MealPlan.query.filter_by(id=meal_id, user_id=user_id).first()

    if meal is None:
        return jsonify({"error": "Meal not found"}), 404

    return jsonify(meal.to_dict()), 200


@meal_bp.route("/<int:meal_id>", methods=["DELETE"])
@jwt_required()
def delete_meal(meal_id):
    """Delete a meal from today's plan."""
    user_id = int(get_jwt_identity())
    meal = MealPlan.query.filter_by(id=meal_id, user_id=user_id).first()

    if meal is None:
        return jsonify({"error": "Meal not found"}), 404

    db.session.delete(meal)
    db.session.commit()

    return jsonify({"message": "Meal deleted successfully"}), 200



@meal_bp.route("/refresh", methods=["POST"])
@jwt_required()
def refresh_meals():
    """Re-generate today's meal plan using latest profile preferences."""
    user_id = int(get_jwt_identity())
    profile = Profile.query.filter_by(user_id=user_id).first()

    generate_meal_plan(user_id, profile)

    meals = MealPlan.query.filter_by(user_id=user_id, date=date.today()).all()
    grouped = {"breakfast": [], "lunch": [], "dinner": [], "snack": []}
    for m in meals:
        grouped.setdefault(m.meal_type, []).append(m.to_dict())

    return jsonify({"message": "Meals refreshed", "meals": grouped}), 200


@meal_bp.route("/search", methods=["GET"])
@jwt_required()
def search_meals():
    """Search meals by title."""
    user_id = int(get_jwt_identity())
    query = request.args.get("q", "").strip().lower()

    if not query:
        return jsonify([]), 200

    meals = MealPlan.query.filter(
        MealPlan.user_id == user_id,
        MealPlan.title.ilike(f"%{query}%"),
    ).all()

    return jsonify([m.to_dict() for m in meals]), 200

@meal_bp.route("/save", methods=["POST"])
@jwt_required()
def save_meal():
    """Save an AI recommendation to today's meal plan."""
    user_id = int(get_jwt_identity())
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    meal_type = data.get("meal_type", "snack").lower()
    
    date_str = data.get("date")
    if date_str:
        try:
            today = date.fromisoformat(date_str)
        except ValueError:
            today = date.today()
    else:
        today = date.today()

    # Delete any existing meal for the date of the same type to support replacement
    MealPlan.query.filter_by(user_id=user_id, date=today, meal_type=meal_type).delete()

    meal = MealPlan(
        user_id=user_id,
        meal_type=meal_type,
        title=data.get("title", "Saved Meal"),
        calories=int(data.get("calories", 0)),
        protein=float(data.get("protein", 0)),
        carbs=float(data.get("carbs", 0)),
        fat=float(data.get("fat", 0)),
        ingredients=data.get("ingredients", ""),
        recipe_steps=data.get("recipe_steps", ""),
        health_benefits=data.get("health_benefits", ""),
        recommendation_reason=data.get("recommendation_reason", "Recommended based on your health goals."),
        date=today
    )
    db.session.add(meal)
    db.session.commit()
    
    return jsonify({"message": "Meal saved successfully", "meal": meal.to_dict()}), 201


@meal_bp.route("/replace", methods=["POST"])
@jwt_required()
def replace_meal():
    """Replace a meal for a specific category and date with another AI recommendation."""
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}
    meal_type = data.get("meal_type", "snack").lower()
    
    date_str = data.get("date")
    if date_str:
        try:
            today = date.fromisoformat(date_str)
        except ValueError:
            today = date.today()
    else:
        today = date.today()

    profile = Profile.query.filter_by(user_id=user_id).first()
    diet = profile.diet if profile else "Vegetarian"
    goal = profile.goal if profile else "Maintenance"
    age = profile.age if profile else 25

    # Get recommendations from hybrid engine
    from recommendation.hybrid_engine import recommend
    result = recommend(
        user_id=user_id,
        diet=diet,
        goal=goal,
        age=age,
        meal_type=meal_type,
        top_k=5
    )
    recs = result.get("recommendations", [])
    if not recs:
        return jsonify({"error": "No replacements found"}), 404

    # Find the current meal title to avoid picking the same one
    current_meal = MealPlan.query.filter_by(user_id=user_id, date=today, meal_type=meal_type).first()
    current_title = current_meal.title if current_meal else ""

    # Filter out current meal
    choices = [r for r in recs if r["title"] != current_title]
    if not choices:
        choices = recs

    new_meal_data = random.choice(choices)

    # Delete existing
    MealPlan.query.filter_by(user_id=user_id, date=today, meal_type=meal_type).delete()

    # Save new meal
    new_meal = MealPlan(
        user_id=user_id,
        meal_type=meal_type,
        title=new_meal_data["title"],
        calories=new_meal_data["calories"],
        protein=new_meal_data["protein"],
        carbs=new_meal_data["carbs"],
        fat=new_meal_data["fat"],
        ingredients=new_meal_data["ingredients"],
        recipe_steps=new_meal_data["recipe_steps"],
        health_benefits=new_meal_data["health_benefits"],
        recommendation_reason=new_meal_data.get("recommendation_reason", "Recommended based on your health goals."),
        date=today
    )
    db.session.add(new_meal)
    db.session.commit()

    return jsonify({"message": "Meal replaced successfully", "meal": new_meal.to_dict()}), 200
