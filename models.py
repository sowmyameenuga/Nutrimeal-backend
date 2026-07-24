from datetime import datetime, date, timezone
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


# ─── User ────────────────────────────────────────────────────────────────────
class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    profile = db.relationship("Profile", backref="user", uselist=False, cascade="all, delete-orphan")
    meal_plans = db.relationship("MealPlan", backref="user", lazy=True, cascade="all, delete-orphan")
    progress_logs = db.relationship("ProgressLog", backref="user", lazy=True, cascade="all, delete-orphan")
    logged_meals = db.relationship("LoggedMeal", backref="user", lazy=True, cascade="all, delete-orphan")

    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


# ─── Profile ─────────────────────────────────────────────────────────────────
class Profile(db.Model):
    __tablename__ = "profiles"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, unique=True)
    age = db.Column(db.Integer)
    gender = db.Column(db.String(20))
    height_cm = db.Column(db.Float)
    weight_kg = db.Column(db.Float)
    goal = db.Column(db.String(50))
    allergy = db.Column(db.String(50))
    diet = db.Column(db.String(30), default="Veg")  # Veg / Non-Veg / Vegan
    country = db.Column(db.String(50))

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "name": self.user.name if self.user else None,
            "age": self.age,
            "gender": self.gender,
            "height_cm": self.height_cm,
            "weight_kg": self.weight_kg,
            "goal": self.goal,
            "allergy": self.allergy,
            "diet": self.diet,
            "country": self.country,
        }


# ─── Meal Plan ───────────────────────────────────────────────────────────────
class MealPlan(db.Model):
    __tablename__ = "meal_plans"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    meal_type = db.Column(db.String(20), nullable=False)  # breakfast, lunch, dinner
    title = db.Column(db.String(200), nullable=False)
    calories = db.Column(db.Integer, default=0)
    protein = db.Column(db.Float, default=0)
    carbs = db.Column(db.Float, default=0)
    fat = db.Column(db.Float, default=0)
    ingredients = db.Column(db.Text, default="")
    health_benefits = db.Column(db.Text, default="")
    recipe_steps = db.Column(db.Text, default="")
    date = db.Column(db.Date, default=date.today)
    eaten = db.Column(db.Boolean, default=False)
    completion_time = db.Column(db.String(50), nullable=True)
    recommendation_reason = db.Column(db.Text, default="")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "meal_type": self.meal_type,
            "title": self.title,
            "calories": self.calories if self.calories is not None else 0,
            "protein": self.protein if self.protein is not None else 0.0,
            "carbs": self.carbs if self.carbs is not None else 0.0,
            "fat": self.fat if self.fat is not None else 0.0,
            "ingredients": self.ingredients if self.ingredients else "",
            "health_benefits": self.health_benefits if self.health_benefits else "",
            "recipe_steps": self.recipe_steps if self.recipe_steps else "",
            "date": self.date.isoformat() if self.date else None,
            "eaten": self.eaten,
            "completion_time": self.completion_time,
            "recommendation_reason": self.recommendation_reason if self.recommendation_reason else "Recommended based on your health goals.",
        }


# ─── Progress Log ────────────────────────────────────────────────────────────
class ProgressLog(db.Model):
    __tablename__ = "progress_logs"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    date = db.Column(db.Date, default=date.today)
    calories_consumed = db.Column(db.Integer, default=0)
    protein_consumed = db.Column(db.Float, default=0)
    water_litres = db.Column(db.Float, default=0)
    current_weight = db.Column(db.Float, default=0)

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "date": self.date.isoformat() if self.date else None,
            "calories_consumed": self.calories_consumed,
            "protein_consumed": self.protein_consumed,
            "water_litres": self.water_litres,
            "current_weight": self.current_weight,
        }


# ─── Logged Meal ─────────────────────────────────────────────────────────────
class LoggedMeal(db.Model):
    __tablename__ = "logged_meals"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    meal_id = db.Column(db.Integer, nullable=True) # Optional link to meal plan or recipe id
    title = db.Column(db.String(200), nullable=False)
    calories = db.Column(db.Integer, default=0)
    protein = db.Column(db.Float, default=0)
    carbs = db.Column(db.Float, default=0)
    fat = db.Column(db.Float, default=0)
    date = db.Column(db.Date, default=date.today)

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "meal_id": self.meal_id,
            "title": self.title,
            "calories": self.calories,
            "protein": self.protein,
            "carbs": self.carbs,
            "fat": self.fat,
            "date": self.date.isoformat() if self.date else None,
        }
