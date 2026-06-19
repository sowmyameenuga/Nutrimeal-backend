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

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "meal_type": self.meal_type,
            "title": self.title,
            "calories": self.calories,
            "protein": self.protein,
            "carbs": self.carbs,
            "fat": self.fat,
            "ingredients": self.ingredients,
            "health_benefits": self.health_benefits,
            "recipe_steps": self.recipe_steps,
            "date": self.date.isoformat() if self.date else None,
        }


# ─── Progress Log ────────────────────────────────────────────────────────────
class ProgressLog(db.Model):
    __tablename__ = "progress_logs"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    date = db.Column(db.Date, default=date.today)
    calories_consumed = db.Column(db.Integer, default=0)
    water_litres = db.Column(db.Float, default=0)
    current_weight = db.Column(db.Float, default=0)

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "date": self.date.isoformat() if self.date else None,
            "calories_consumed": self.calories_consumed,
            "water_litres": self.water_litres,
            "current_weight": self.current_weight,
        }
