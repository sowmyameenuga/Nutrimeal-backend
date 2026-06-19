"""
Synthetic Dataset Generator for AI Nutrition Recommendation System.
Generates realistic food, user, and interaction datasets.

Run: python data/generate_datasets.py
"""
import csv
import os
import random
from datetime import datetime, timedelta

random.seed(42)

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# ═══════════════════════════════════════════════════════════════════════════════
#  FOOD DATASET — 150 items
# ═══════════════════════════════════════════════════════════════════════════════

FOODS = [
    # ── BREAKFAST — Vegan (15) ──────────────────────────────────────────────
    (1, "Oats with Berries", 310, 12, 48, 8, 7, "Vegan", "Breakfast", "All"),
    (2, "Banana Almond Smoothie", 280, 8, 38, 10, 4, "Vegan", "Breakfast", "Maintenance"),
    (3, "Avocado Toast (Sourdough)", 340, 10, 30, 20, 6, "Vegan", "Breakfast", "Maintenance"),
    (4, "Overnight Chia Pudding", 260, 9, 32, 12, 9, "Vegan", "Breakfast", "Weight Loss"),
    (5, "Peanut Butter Banana Wrap", 380, 14, 45, 16, 5, "Vegan", "Breakfast", "Muscle Gain"),
    (6, "Fruit & Granola Bowl", 320, 7, 55, 9, 6, "Vegan", "Breakfast", "All"),
    (7, "Tofu Scramble", 220, 18, 10, 12, 3, "Vegan", "Breakfast", "Weight Loss"),
    (8, "Green Detox Smoothie", 180, 5, 30, 4, 5, "Vegan", "Breakfast", "Weight Loss"),
    (9, "Mango Coconut Porridge", 340, 8, 50, 12, 4, "Vegan", "Breakfast", "Maintenance"),
    (10, "Vegan Protein Pancakes", 350, 20, 40, 10, 5, "Vegan", "Breakfast", "Muscle Gain"),
    # ── BREAKFAST — Vegetarian (10) ─────────────────────────────────────────
    (11, "Egg White Omelette", 180, 22, 8, 6, 2, "Vegetarian", "Breakfast", "Weight Loss"),
    (12, "Paneer Paratha", 420, 16, 38, 22, 3, "Vegetarian", "Breakfast", "Muscle Gain"),
    (13, "Greek Yogurt Parfait", 290, 18, 35, 8, 3, "Vegetarian", "Breakfast", "All"),
    (14, "Masala Dosa", 350, 8, 50, 14, 4, "Vegetarian", "Breakfast", "Maintenance"),
    (15, "Cheese Omelette", 310, 24, 4, 22, 1, "Vegetarian", "Breakfast", "Muscle Gain"),
    (16, "Idli Sambar", 250, 10, 42, 4, 5, "Vegetarian", "Breakfast", "Weight Loss"),
    (17, "Poha with Peanuts", 280, 8, 40, 10, 3, "Vegetarian", "Breakfast", "All"),
    (18, "Upma", 240, 7, 38, 7, 3, "Vegetarian", "Breakfast", "Weight Loss"),
    (19, "Egg Bhurji on Toast", 340, 20, 28, 16, 3, "Vegetarian", "Breakfast", "Maintenance"),
    (20, "Stuffed Paratha with Curd", 400, 14, 45, 18, 4, "Vegetarian", "Breakfast", "Muscle Gain"),
    # ── BREAKFAST — Non-Vegetarian (10) ─────────────────────────────────────
    (21, "Chicken Sausage Wrap", 380, 26, 30, 16, 2, "Non-Vegetarian", "Breakfast", "Muscle Gain"),
    (22, "Smoked Salmon Bagel", 420, 28, 35, 18, 2, "Non-Vegetarian", "Breakfast", "Muscle Gain"),
    (23, "Turkey Bacon & Eggs", 350, 30, 8, 22, 1, "Non-Vegetarian", "Breakfast", "Muscle Gain"),
    (24, "Chicken Keema Toast", 360, 24, 28, 16, 2, "Non-Vegetarian", "Breakfast", "Maintenance"),
    (25, "Egg & Chicken Burrito", 450, 32, 35, 20, 3, "Non-Vegetarian", "Breakfast", "Muscle Gain"),
    (26, "Prawn Omelette", 240, 26, 6, 12, 1, "Non-Vegetarian", "Breakfast", "Weight Loss"),
    (27, "Mutton Keema Paratha", 480, 22, 40, 26, 3, "Non-Vegetarian", "Breakfast", "Muscle Gain"),
    (28, "Egg Fried Rice", 380, 16, 50, 14, 2, "Non-Vegetarian", "Breakfast", "Maintenance"),
    (29, "Ham & Cheese Sandwich", 400, 24, 32, 20, 2, "Non-Vegetarian", "Breakfast", "Maintenance"),
    (30, "Boiled Eggs & Avocado", 280, 20, 8, 20, 5, "Non-Vegetarian", "Breakfast", "Weight Loss"),

    # ── LUNCH — Vegan (13) ──────────────────────────────────────────────────
    (31, "Quinoa Veg Bowl", 420, 18, 60, 12, 8, "Vegan", "Lunch", "All"),
    (32, "Lentil Soup", 320, 22, 45, 5, 12, "Vegan", "Lunch", "Weight Loss"),
    (33, "Chickpea Curry with Rice", 480, 20, 65, 14, 10, "Vegan", "Lunch", "Maintenance"),
    (34, "Falafel Wrap", 420, 16, 48, 18, 7, "Vegan", "Lunch", "All"),
    (35, "Black Bean Burrito Bowl", 450, 20, 55, 14, 12, "Vegan", "Lunch", "All"),
    (36, "Vegetable Stir-Fry with Tofu", 360, 22, 30, 16, 6, "Vegan", "Lunch", "Weight Loss"),
    (37, "Rajma Chawal", 440, 18, 62, 10, 11, "Vegan", "Lunch", "Maintenance"),
    (38, "Sweet Potato & Kale Salad", 320, 10, 45, 12, 7, "Vegan", "Lunch", "Weight Loss"),
    (39, "Mushroom Risotto (Vegan)", 400, 12, 58, 14, 4, "Vegan", "Lunch", "Maintenance"),
    (40, "Chole with Brown Rice", 460, 18, 64, 12, 10, "Vegan", "Lunch", "All"),
    (41, "Vegan Buddha Bowl", 380, 16, 48, 14, 9, "Vegan", "Lunch", "Weight Loss"),
    (42, "Dal Tadka with Roti", 400, 18, 52, 12, 8, "Vegan", "Lunch", "All"),
    (43, "Peanut Noodle Stir-Fry", 440, 16, 50, 20, 5, "Vegan", "Lunch", "Maintenance"),
    # ── LUNCH — Vegetarian (12) ─────────────────────────────────────────────
    (44, "Paneer Butter Masala + Rice", 520, 22, 55, 24, 4, "Vegetarian", "Lunch", "Muscle Gain"),
    (45, "Palak Paneer with Naan", 480, 20, 42, 26, 5, "Vegetarian", "Lunch", "Muscle Gain"),
    (46, "Veg Biryani", 450, 14, 60, 16, 5, "Vegetarian", "Lunch", "Maintenance"),
    (47, "Paneer Tikka Wrap", 400, 22, 35, 18, 4, "Vegetarian", "Lunch", "All"),
    (48, "Cheese Grilled Sandwich", 380, 18, 32, 20, 3, "Vegetarian", "Lunch", "Maintenance"),
    (49, "Egg Curry with Rice", 440, 22, 50, 16, 3, "Vegetarian", "Lunch", "All"),
    (50, "Aloo Gobi with Roti", 360, 10, 50, 14, 6, "Vegetarian", "Lunch", "Weight Loss"),
    (51, "Curd Rice", 300, 10, 48, 8, 2, "Vegetarian", "Lunch", "Weight Loss"),
    (52, "Thali (Mixed Veg)", 500, 18, 60, 20, 8, "Vegetarian", "Lunch", "Maintenance"),
    (53, "Vegetable Pulao", 380, 10, 55, 12, 5, "Vegetarian", "Lunch", "All"),
    (54, "Khichdi", 320, 14, 48, 8, 6, "Vegetarian", "Lunch", "Weight Loss"),
    (55, "Pav Bhaji", 420, 12, 52, 18, 6, "Vegetarian", "Lunch", "Maintenance"),
    # ── LUNCH — Non-Vegetarian (13) ─────────────────────────────────────────
    (56, "Grilled Chicken Salad", 380, 35, 20, 16, 5, "Non-Vegetarian", "Lunch", "Weight Loss"),
    (57, "Chicken Biryani", 550, 30, 60, 20, 3, "Non-Vegetarian", "Lunch", "Muscle Gain"),
    (58, "Fish Curry with Rice", 480, 32, 50, 16, 3, "Non-Vegetarian", "Lunch", "All"),
    (59, "Tuna Poke Bowl", 420, 32, 45, 14, 4, "Non-Vegetarian", "Lunch", "All"),
    (60, "Lamb Kofta with Hummus", 500, 28, 30, 28, 4, "Non-Vegetarian", "Lunch", "Muscle Gain"),
    (61, "Chicken Shawarma Plate", 480, 30, 40, 20, 3, "Non-Vegetarian", "Lunch", "Maintenance"),
    (62, "Prawn Fried Rice", 440, 24, 52, 16, 2, "Non-Vegetarian", "Lunch", "Maintenance"),
    (63, "Butter Chicken + Naan", 580, 30, 45, 30, 3, "Non-Vegetarian", "Lunch", "Muscle Gain"),
    (64, "Grilled Fish Tacos", 400, 28, 35, 16, 4, "Non-Vegetarian", "Lunch", "All"),
    (65, "Chicken Caesar Salad", 420, 32, 18, 24, 3, "Non-Vegetarian", "Lunch", "Weight Loss"),
    (66, "Mutton Rogan Josh + Rice", 560, 28, 55, 26, 3, "Non-Vegetarian", "Lunch", "Muscle Gain"),
    (67, "Egg Fried Noodles", 400, 18, 48, 16, 3, "Non-Vegetarian", "Lunch", "Maintenance"),
    (68, "Tandoori Chicken with Roti", 420, 34, 32, 14, 3, "Non-Vegetarian", "Lunch", "All"),

    # ── DINNER — Vegan (12) ─────────────────────────────────────────────────
    (69, "Stir-Fry Tofu & Vegetables", 340, 20, 30, 14, 6, "Vegan", "Dinner", "Weight Loss"),
    (70, "Baked Sweet Potato Bowl", 360, 14, 52, 10, 8, "Vegan", "Dinner", "All"),
    (71, "Vegetable Thai Curry", 380, 12, 40, 18, 5, "Vegan", "Dinner", "Maintenance"),
    (72, "Stuffed Bell Peppers", 300, 14, 35, 12, 6, "Vegan", "Dinner", "Weight Loss"),
    (73, "Mushroom & Spinach Pasta", 400, 14, 52, 16, 5, "Vegan", "Dinner", "Maintenance"),
    (74, "Cauliflower Rice Bowl", 260, 12, 22, 14, 6, "Vegan", "Dinner", "Weight Loss"),
    (75, "Vegan Chili", 350, 18, 42, 10, 12, "Vegan", "Dinner", "All"),
    (76, "Roasted Vegetable Soup", 220, 8, 30, 8, 6, "Vegan", "Dinner", "Weight Loss"),
    (77, "Pad Thai (Vegan)", 420, 14, 55, 16, 4, "Vegan", "Dinner", "Maintenance"),
    (78, "Moong Dal Khichdi", 320, 16, 48, 6, 7, "Vegan", "Dinner", "Weight Loss"),
    (79, "Vegetable Sushi Rolls", 280, 8, 45, 6, 4, "Vegan", "Dinner", "Weight Loss"),
    (80, "Jackfruit Tacos", 340, 10, 42, 14, 6, "Vegan", "Dinner", "All"),
    # ── DINNER — Vegetarian (13) ────────────────────────────────────────────
    (81, "Grilled Paneer Salad", 380, 24, 18, 22, 4, "Vegetarian", "Dinner", "Weight Loss"),
    (82, "Paneer Tikka Masala", 440, 22, 28, 28, 4, "Vegetarian", "Dinner", "Muscle Gain"),
    (83, "Pasta Alfredo", 480, 18, 50, 24, 3, "Vegetarian", "Dinner", "Maintenance"),
    (84, "Vegetable Lasagna", 420, 20, 42, 20, 5, "Vegetarian", "Dinner", "All"),
    (85, "Egg Drop Soup + Fried Rice", 380, 16, 48, 14, 3, "Vegetarian", "Dinner", "Maintenance"),
    (86, "Shahi Paneer with Roti", 460, 20, 35, 28, 3, "Vegetarian", "Dinner", "Muscle Gain"),
    (87, "Cottage Cheese Salad", 280, 22, 14, 16, 4, "Vegetarian", "Dinner", "Weight Loss"),
    (88, "Mushroom Stroganoff", 400, 14, 40, 20, 4, "Vegetarian", "Dinner", "Maintenance"),
    (89, "Spinach & Ricotta Crepes", 350, 18, 30, 18, 3, "Vegetarian", "Dinner", "All"),
    (90, "Baingan Bharta + Roti", 320, 10, 38, 14, 6, "Vegetarian", "Dinner", "Weight Loss"),
    (91, "Malai Kofta", 480, 16, 40, 30, 3, "Vegetarian", "Dinner", "Muscle Gain"),
    (92, "Mixed Veg Curry + Rice", 420, 14, 56, 14, 6, "Vegetarian", "Dinner", "All"),
    (93, "Cheese Pizza (Thin Crust)", 440, 18, 45, 22, 3, "Vegetarian", "Dinner", "Maintenance"),
    # ── DINNER — Non-Vegetarian (13) ────────────────────────────────────────
    (94, "Grilled Salmon + Asparagus", 450, 38, 12, 28, 4, "Non-Vegetarian", "Dinner", "All"),
    (95, "Chicken Stir-Fry", 380, 32, 25, 14, 4, "Non-Vegetarian", "Dinner", "Weight Loss"),
    (96, "Fish Tikka", 300, 30, 10, 16, 2, "Non-Vegetarian", "Dinner", "Weight Loss"),
    (97, "Chicken Soup", 220, 24, 15, 8, 2, "Non-Vegetarian", "Dinner", "Weight Loss"),
    (98, "Lamb Chops with Veggies", 520, 36, 12, 36, 3, "Non-Vegetarian", "Dinner", "Muscle Gain"),
    (99, "Baked Cod with Quinoa", 380, 32, 35, 10, 5, "Non-Vegetarian", "Dinner", "All"),
    (100, "Chicken Tikka Masala", 480, 30, 30, 26, 3, "Non-Vegetarian", "Dinner", "Maintenance"),
    (101, "Shrimp Garlic Pasta", 460, 26, 48, 18, 3, "Non-Vegetarian", "Dinner", "Maintenance"),
    (102, "Mutton Biryani", 580, 28, 60, 26, 3, "Non-Vegetarian", "Dinner", "Muscle Gain"),
    (103, "Grilled Turkey Breast", 300, 36, 8, 12, 2, "Non-Vegetarian", "Dinner", "Weight Loss"),
    (104, "Chicken Kebab Plate", 400, 34, 20, 20, 3, "Non-Vegetarian", "Dinner", "All"),
    (105, "Egg Curry with Chapati", 380, 20, 35, 18, 4, "Non-Vegetarian", "Dinner", "All"),
    (106, "Prawn Masala + Rice", 440, 28, 48, 14, 3, "Non-Vegetarian", "Dinner", "Maintenance"),

    # ── SNACK — Vegan (15) ──────────────────────────────────────────────────
    (107, "Mixed Nuts Trail Mix", 250, 8, 18, 18, 4, "Vegan", "Snack", "Muscle Gain"),
    (108, "Apple Slices with PB", 220, 6, 28, 10, 4, "Vegan", "Snack", "All"),
    (109, "Hummus & Carrot Sticks", 180, 6, 20, 8, 5, "Vegan", "Snack", "Weight Loss"),
    (110, "Roasted Chickpeas", 200, 10, 28, 6, 8, "Vegan", "Snack", "Weight Loss"),
    (111, "Energy Date Balls", 240, 6, 35, 10, 4, "Vegan", "Snack", "All"),
    (112, "Fruit Salad Bowl", 150, 3, 35, 1, 4, "Vegan", "Snack", "Weight Loss"),
    (113, "Edamame Beans", 180, 16, 12, 8, 5, "Vegan", "Snack", "Muscle Gain"),
    (114, "Vegan Protein Bar", 220, 18, 22, 8, 3, "Vegan", "Snack", "Muscle Gain"),
    (115, "Popcorn (Air-Popped)", 120, 4, 22, 2, 4, "Vegan", "Snack", "Weight Loss"),
    (116, "Sweet Potato Fries (Baked)", 200, 3, 35, 6, 4, "Vegan", "Snack", "All"),
    (117, "Makhana (Fox Nuts)", 160, 5, 26, 4, 2, "Vegan", "Snack", "Weight Loss"),
    (118, "Coconut Ladoo (Vegan)", 200, 3, 24, 12, 3, "Vegan", "Snack", "Maintenance"),
    (119, "Sprout Chaat", 180, 10, 24, 4, 6, "Vegan", "Snack", "Weight Loss"),
    (120, "Vegan Smoothie Bowl", 260, 8, 40, 8, 5, "Vegan", "Snack", "All"),
    (121, "Rice Cakes with Avocado", 190, 4, 24, 8, 3, "Vegan", "Snack", "Weight Loss"),
    # ── SNACK — Vegetarian (15) ─────────────────────────────────────────────
    (122, "Greek Yogurt with Honey", 200, 14, 24, 6, 1, "Vegetarian", "Snack", "All"),
    (123, "Paneer Tikka Bites", 240, 18, 8, 16, 1, "Vegetarian", "Snack", "Muscle Gain"),
    (124, "Cheese & Crackers", 220, 10, 18, 14, 1, "Vegetarian", "Snack", "Maintenance"),
    (125, "Protein Shake (Whey)", 180, 25, 8, 4, 1, "Vegetarian", "Snack", "Muscle Gain"),
    (126, "Dhokla", 180, 6, 28, 5, 2, "Vegetarian", "Snack", "Weight Loss"),
    (127, "Cottage Cheese Bites", 160, 16, 6, 8, 1, "Vegetarian", "Snack", "Weight Loss"),
    (128, "Banana Milkshake", 260, 10, 38, 8, 2, "Vegetarian", "Snack", "Maintenance"),
    (129, "Egg Sandwich", 300, 18, 28, 14, 2, "Vegetarian", "Snack", "All"),
    (130, "Raita with Boondi", 140, 6, 16, 6, 1, "Vegetarian", "Snack", "Weight Loss"),
    (131, "Samosa (Baked)", 220, 6, 28, 10, 3, "Vegetarian", "Snack", "Maintenance"),
    (132, "Lassi (Sweet)", 200, 8, 30, 6, 0, "Vegetarian", "Snack", "Maintenance"),
    (133, "Cheese Stuffed Mushrooms", 200, 12, 8, 14, 2, "Vegetarian", "Snack", "All"),
    (134, "Khandvi", 160, 8, 20, 6, 2, "Vegetarian", "Snack", "Weight Loss"),
    (135, "Masala Chaas", 80, 4, 8, 3, 1, "Vegetarian", "Snack", "Weight Loss"),
    (136, "Bread Pakora", 280, 8, 30, 14, 2, "Vegetarian", "Snack", "Maintenance"),
    # ── SNACK — Non-Vegetarian (14) ─────────────────────────────────────────
    (137, "Chicken Wings (Grilled)", 280, 24, 4, 18, 1, "Non-Vegetarian", "Snack", "Muscle Gain"),
    (138, "Boiled Eggs", 140, 12, 2, 10, 0, "Non-Vegetarian", "Snack", "Weight Loss"),
    (139, "Tuna Salad Cup", 200, 22, 8, 10, 2, "Non-Vegetarian", "Snack", "Weight Loss"),
    (140, "Chicken Momos", 260, 18, 24, 10, 2, "Non-Vegetarian", "Snack", "All"),
    (141, "Fish Fingers (Baked)", 240, 20, 18, 10, 1, "Non-Vegetarian", "Snack", "All"),
    (142, "Beef Jerky", 180, 26, 6, 6, 1, "Non-Vegetarian", "Snack", "Muscle Gain"),
    (143, "Chicken Seekh Kebab", 220, 22, 8, 12, 1, "Non-Vegetarian", "Snack", "Muscle Gain"),
    (144, "Prawn Crackers", 180, 8, 22, 8, 1, "Non-Vegetarian", "Snack", "Maintenance"),
    (145, "Egg Roll", 300, 16, 28, 14, 2, "Non-Vegetarian", "Snack", "All"),
    (146, "Smoked Chicken Bites", 200, 24, 4, 10, 1, "Non-Vegetarian", "Snack", "Weight Loss"),
    (147, "Lamb Samosa", 280, 12, 24, 16, 2, "Non-Vegetarian", "Snack", "Maintenance"),
    (148, "Chicken Salad Wrap", 320, 26, 24, 14, 3, "Non-Vegetarian", "Snack", "All"),
    (149, "Egg Muffin", 240, 16, 18, 12, 1, "Non-Vegetarian", "Snack", "Maintenance"),
    (150, "Tandoori Prawns", 200, 24, 6, 10, 1, "Non-Vegetarian", "Snack", "Weight Loss"),
]

FOOD_HEADER = [
    "item_id", "name", "calories", "protein", "carbs",
    "fat", "fiber", "diet_type", "meal_type", "goal_tag",
]


# ═══════════════════════════════════════════════════════════════════════════════
#  USER DATASET — 50 synthetic users
# ═══════════════════════════════════════════════════════════════════════════════

DIETS = ["Vegetarian", "Non-Vegetarian", "Vegan"]
GOALS = ["Weight Loss", "Muscle Gain", "Maintenance"]
GENDERS = ["Male", "Female"]


def generate_users(n=50):
    users = []
    for uid in range(1, n + 1):
        age = random.randint(18, 55)
        gender = random.choice(GENDERS)
        diet = random.choices(DIETS, weights=[40, 40, 20])[0]  # realistic distribution
        goal = random.choice(GOALS)
        users.append((uid, age, gender, diet, goal))
    return users


USER_HEADER = ["user_id", "age", "gender", "diet", "goal"]


# ═══════════════════════════════════════════════════════════════════════════════
#  INTERACTION DATASET — 1500+ rows
# ═══════════════════════════════════════════════════════════════════════════════

# Diet compatibility mapping
DIET_COMPAT = {
    "Vegan": {"Vegan"},
    "Vegetarian": {"Vegan", "Vegetarian"},
    "Non-Vegetarian": {"Vegan", "Vegetarian", "Non-Vegetarian"},
}


def generate_interactions(users, foods, min_rows=1500):
    """
    Generate realistic user-food interactions.
    Rules:
      - Users only interact with diet-compatible foods
      - Higher ratings for goal-matching foods
      - Temporal patterns (meal_type ↔ time of day)
      - Each user interacts with 25-45 food items
    """
    interactions = []
    food_by_id = {f[0]: f for f in foods}

    base_date = datetime(2026, 1, 1)

    for user in users:
        uid, age, gender, diet, goal = user
        compatible_ids = [
            f[0] for f in foods if f[7] in DIET_COMPAT[diet]
        ]

        # Each user interacts with 25-45 items
        n_interactions = random.randint(28, 45)
        if n_interactions > len(compatible_ids):
            n_interactions = len(compatible_ids)

        sampled_ids = random.sample(compatible_ids, n_interactions)

        for item_id in sampled_ids:
            food = food_by_id[item_id]
            food_goal = food[9]    # goal_tag
            food_meal = food[8]    # meal_type
            food_cal = food[2]     # calories

            # ── Base rating logic ──
            base_rating = 3

            # Goal match bonus
            if food_goal == goal or food_goal == "All":
                base_rating += 1

            # Calorie preference
            if goal == "Weight Loss" and food_cal <= 350:
                base_rating += 1
            elif goal == "Muscle Gain" and food[3] >= 20:  # protein
                base_rating += 1

            # Add noise
            rating = base_rating + random.choice([-1, 0, 0, 0, 1])
            rating = max(1, min(5, rating))

            # Liked: based on rating
            liked = 1 if rating >= 4 else (0 if rating <= 2 else random.choice([0, 1]))

            # Clicked: always 1 (they interacted), but 10% chance of click-only
            clicked = 1

            # Timestamp based on meal type
            day_offset = random.randint(0, 150)
            if food_meal == "Breakfast":
                hour = random.randint(6, 9)
            elif food_meal == "Lunch":
                hour = random.randint(11, 14)
            elif food_meal == "Dinner":
                hour = random.randint(18, 21)
            else:  # Snack
                hour = random.choice([10, 11, 15, 16, 17, 22])

            ts = base_date + timedelta(days=day_offset, hours=hour,
                                       minutes=random.randint(0, 59))

            interactions.append((
                uid, item_id, rating, liked, clicked,
                ts.strftime("%Y-%m-%d %H:%M:%S"),
            ))

    # Ensure minimum rows by adding extra interactions for random users
    while len(interactions) < min_rows:
        user = random.choice(users)
        uid, _, _, diet, goal = user
        compatible_ids = [f[0] for f in foods if f[7] in DIET_COMPAT[diet]]
        item_id = random.choice(compatible_ids)
        food = food_by_id[item_id]

        rating = random.randint(2, 5)
        liked = 1 if rating >= 4 else random.choice([0, 1])
        day_offset = random.randint(0, 150)
        hour = random.randint(6, 22)
        ts = base_date + timedelta(days=day_offset, hours=hour,
                                   minutes=random.randint(0, 59))

        interactions.append((
            uid, item_id, rating, liked, 1,
            ts.strftime("%Y-%m-%d %H:%M:%S"),
        ))

    random.shuffle(interactions)
    return interactions


INTERACTION_HEADER = [
    "user_id", "item_id", "rating", "liked", "clicked", "timestamp",
]


# ═══════════════════════════════════════════════════════════════════════════════
#  MAIN — Generate and save all CSVs
# ═══════════════════════════════════════════════════════════════════════════════

def write_csv(filepath, header, rows):
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(rows)
    print(f"  -> {filepath}: {len(rows)} rows")


def main():
    print("Generating datasets...")

    # Foods
    food_path = os.path.join(SCRIPT_DIR, "food_dataset.csv")
    write_csv(food_path, FOOD_HEADER, FOODS)

    # Users
    users = generate_users(50)
    user_path = os.path.join(SCRIPT_DIR, "user_dataset.csv")
    write_csv(user_path, USER_HEADER, users)

    # Interactions
    interactions = generate_interactions(users, FOODS, min_rows=1500)
    interaction_path = os.path.join(SCRIPT_DIR, "interaction_dataset.csv")
    write_csv(interaction_path, INTERACTION_HEADER, interactions)

    print(f"\nDone! Generated:")
    print(f"  Foods: {len(FOODS)} items")
    print(f"  Users: {len(users)} users")
    print(f"  Interactions: {len(interactions)} rows")

    # Stats
    diets = {}
    for f in FOODS:
        diets[f[7]] = diets.get(f[7], 0) + 1
    print(f"\nFood diet distribution: {diets}")

    meals = {}
    for f in FOODS:
        meals[f[8]] = meals.get(f[8], 0) + 1
    print(f"Food meal distribution: {meals}")


if __name__ == "__main__":
    main()
