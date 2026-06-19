"""
Seed the database with sample data for development/demo.
Run: python seed_data.py
"""
from datetime import date, timedelta
from app import create_app
from models import db, User, Profile, ProgressLog

app = create_app()


def seed():
    with app.app_context():
        # Check if already seeded
        if User.query.filter_by(email="demo@nutriapp.com").first():
            print("Database already seeded. Skipping.")
            return

        # ── Demo User ──
        user = User(name="Demo User", email="demo@nutriapp.com")
        user.set_password("demo123")
        db.session.add(user)
        db.session.flush()  # get user.id

        # ── Profile ──
        profile = Profile(
            user_id=user.id,
            age=25,
            gender="Male",
            height_cm=175.0,
            weight_kg=70.0,
            goal="Weight Loss",
            allergy="None",
            diet="Veg",
        )
        db.session.add(profile)

        # ── Progress Logs (last 7 days) ──
        sample_data = [
            {"calories": 1800, "water": 2.5, "weight": 70.5},
            {"calories": 1600, "water": 2.8, "weight": 70.3},
            {"calories": 2000, "water": 3.0, "weight": 70.1},
            {"calories": 1700, "water": 2.2, "weight": 70.0},
            {"calories": 1900, "water": 2.7, "weight": 69.8},
            {"calories": 1500, "water": 3.0, "weight": 69.6},
            {"calories": 1200, "water": 2.5, "weight": 69.5},
        ]

        today = date.today()
        for i, data in enumerate(sample_data):
            log = ProgressLog(
                user_id=user.id,
                date=today - timedelta(days=6 - i),
                calories_consumed=data["calories"],
                water_litres=data["water"],
                current_weight=data["weight"],
            )
            db.session.add(log)

        db.session.commit()
        print("Database seeded successfully!")
        print(f"  Demo account: demo@nutriapp.com / demo123")


if __name__ == "__main__":
    seed()
