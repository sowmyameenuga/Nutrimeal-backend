from app import create_app
from models import db, User, ProgressLog
from datetime import date, timedelta
import random

app = create_app()

with app.app_context():
    users = User.query.all()
    today = date.today()
    
    for user in users:
        # Populate the last 6 days (not today)
        for i in range(1, 7):
            d = today - timedelta(days=i)
            # Check if log already exists
            log = ProgressLog.query.filter_by(user_id=user.id, date=d).first()
            if not log:
                # Add mock data
                cals = random.randint(1400, 2400)
                protein = random.randint(50, 150)
                water = round(random.uniform(1.5, 3.5), 1)
                weight = 65.0 + round(random.uniform(-1, 1), 1)
                
                new_log = ProgressLog(
                    user_id=user.id,
                    date=d,
                    calories_consumed=cals,
                    protein_consumed=protein,
                    water_litres=water,
                    current_weight=weight
                )
                db.session.add(new_log)
    
    db.session.commit()
    print("Successfully populated past 6 days of progress for all users!")
