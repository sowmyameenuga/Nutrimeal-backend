import json
import csv
import random
import os

def main():
    root_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(root_dir, 'meal_library_data.json')
    
    with open(json_path, 'r') as f:
        MEAL_LIBRARY = json.load(f)

    # Massive Expansion data
    NEW_MEALS = [
        {"meal_type": "breakfast", "country": "Indian", "title": "Poha with Peanuts", "calories": 300, "protein": 6, "carbs": 50, "fat": 8, "diet_type": "Vegan", "ingredients": "Poha, peanuts, onions, mustard seeds, turmeric", "recipe_steps": "1. Wash poha. 2. Temper mustard seeds. 3. Add onions and peanuts. 4. Mix poha and turmeric.", "health_benefits": "Rich in iron and light on the stomach."},
        {"meal_type": "lunch", "country": "Indian", "title": "Dal Makhani with Jeera Rice", "calories": 550, "protein": 18, "carbs": 75, "fat": 20, "diet_type": "Vegetarian", "ingredients": "Black lentils, kidney beans, butter, cream, cumin, rice", "recipe_steps": "1. Slow cook lentils with spices. 2. Finish with butter and cream. 3. Serve with cumin rice.", "health_benefits": "High protein from lentils and rich complex carbohydrates."},
        {"meal_type": "lunch", "country": "Indian", "title": "Chicken Tikka Masala", "calories": 600, "protein": 35, "carbs": 40, "fat": 30, "diet_type": "Non-Vegetarian", "ingredients": "Chicken breast, yogurt, spices, tomato puree, cream", "recipe_steps": "1. Marinate chicken in yogurt and spices. 2. Grill. 3. Simmer in tomato cream sauce.", "health_benefits": "Excellent source of high-quality protein and metabolism-boosting spices."},
        {"meal_type": "dinner", "country": "Indian", "title": "Palak Paneer", "calories": 400, "protein": 18, "carbs": 15, "fat": 28, "diet_type": "Vegetarian", "ingredients": "Spinach, paneer (cottage cheese), onions, tomatoes, spices", "recipe_steps": "1. Blanch spinach and puree. 2. Saut onions and tomatoes. 3. Add puree and paneer cubes.", "health_benefits": "Packed with iron, calcium, and protein."},
        {"meal_type": "dinner", "country": "Indian", "title": "Fish Curry (Meen Moilee)", "calories": 450, "protein": 30, "carbs": 12, "fat": 25, "diet_type": "Non-Vegetarian", "ingredients": "White fish, coconut milk, curry leaves, turmeric, green chilies", "recipe_steps": "1. Marinate fish. 2. Cook coconut milk with spices. 3. Poach fish in the sauce.", "health_benefits": "Omega-3 fatty acids and heart-healthy coconut fats."},
        
        {"meal_type": "breakfast", "country": "American", "title": "Pancakes with Maple Syrup", "calories": 450, "protein": 10, "carbs": 70, "fat": 15, "diet_type": "Vegetarian", "ingredients": "Flour, milk, eggs, baking powder, maple syrup, butter", "recipe_steps": "1. Mix batter. 2. Cook on griddle until bubbly. 3. Serve with syrup.", "health_benefits": "Quick energy source."},
        {"meal_type": "lunch", "country": "American", "title": "Classic Cheeseburger", "calories": 700, "protein": 35, "carbs": 45, "fat": 40, "diet_type": "Non-Vegetarian", "ingredients": "Beef patty, cheese, bun, lettuce, tomato, pickles", "recipe_steps": "1. Grill patty. 2. Add cheese to melt. 3. Assemble in bun with veggies.", "health_benefits": "High in protein, iron, and B-vitamins."},
        {"meal_type": "dinner", "country": "American", "title": "BBQ Ribs with Coleslaw", "calories": 850, "protein": 40, "carbs": 30, "fat": 60, "diet_type": "Non-Vegetarian", "ingredients": "Pork ribs, BBQ sauce, cabbage, carrots, mayo", "recipe_steps": "1. Slow roast ribs. 2. Glaze with BBQ sauce. 3. Serve with fresh coleslaw.", "health_benefits": "Rich in protein and fat-soluble vitamins."},
        
        {"meal_type": "breakfast", "country": "Italian", "title": "Frittata with Tomatoes & Basil", "calories": 300, "protein": 20, "carbs": 5, "fat": 22, "diet_type": "Vegetarian", "ingredients": "Eggs, cherry tomatoes, fresh basil, parmesan cheese", "recipe_steps": "1. Whisk eggs. 2. Pour into pan with tomatoes. 3. Bake until set. 4. Top with basil.", "health_benefits": "High protein, low carb, rich in lycopene."},
        {"meal_type": "lunch", "country": "Italian", "title": "Margherita Pizza", "calories": 600, "protein": 25, "carbs": 80, "fat": 20, "diet_type": "Vegetarian", "ingredients": "Pizza dough, San Marzano tomatoes, mozzarella, fresh basil", "recipe_steps": "1. Stretch dough. 2. Spread tomatoes and cheese. 3. Bake at high heat. 4. Add basil.", "health_benefits": "Calcium from cheese and antioxidants from tomatoes."},
        {"meal_type": "dinner", "country": "Italian", "title": "Spaghetti Bolognese", "calories": 650, "protein": 30, "carbs": 75, "fat": 22, "diet_type": "Non-Vegetarian", "ingredients": "Spaghetti, ground beef, tomatoes, onions, carrots, celery", "recipe_steps": "1. Brown beef and veggies. 2. Simmer with tomatoes for hours. 3. Toss with pasta.", "health_benefits": "Complete meal with carbs, protein, and vegetable micronutrients."},
        
        {"meal_type": "lunch", "country": "Mexican", "title": "Chicken Fajitas", "calories": 500, "protein": 35, "carbs": 45, "fat": 18, "diet_type": "Non-Vegetarian", "ingredients": "Chicken breast, bell peppers, onions, tortillas, fajita spices", "recipe_steps": "1. Slice chicken and veggies. 2. Stir fry with spices. 3. Serve in warm tortillas.", "health_benefits": "High in vitamin C from peppers and lean protein."},
        {"meal_type": "dinner", "country": "Mexican", "title": "Beef Enchiladas", "calories": 700, "protein": 35, "carbs": 50, "fat": 38, "diet_type": "Non-Vegetarian", "ingredients": "Ground beef, tortillas, enchilada sauce, cheddar cheese", "recipe_steps": "1. Roll beef in tortillas. 2. Cover with sauce and cheese. 3. Bake until bubbly.", "health_benefits": "Comforting meal rich in protein and calcium."},
        {"meal_type": "breakfast", "country": "Mexican", "title": "Huevos Rancheros", "calories": 400, "protein": 18, "carbs": 35, "fat": 22, "diet_type": "Vegetarian", "ingredients": "Eggs, corn tortillas, black beans, salsa, avocado", "recipe_steps": "1. Fry tortillas. 2. Top with warmed beans and fried eggs. 3. Cover with salsa.", "health_benefits": "Excellent balance of fiber, protein, and healthy fats."},
        
        {"meal_type": "lunch", "country": "Asian", "title": "Chicken Teriyaki with Rice", "calories": 550, "protein": 30, "carbs": 85, "fat": 10, "diet_type": "Non-Vegetarian", "ingredients": "Chicken breast, soy sauce, mirin, sugar, rice, broccoli", "recipe_steps": "1. Pan fry chicken. 2. Add teriyaki sauce to glaze. 3. Serve over rice with steamed broccoli.", "health_benefits": "Lean protein and low fat energy source."},
        {"meal_type": "dinner", "country": "Asian", "title": "Tofu Pad Thai", "calories": 480, "protein": 16, "carbs": 65, "fat": 18, "diet_type": "Vegan", "ingredients": "Rice noodles, tofu, peanuts, bean sprouts, tamarind sauce", "recipe_steps": "1. Soak noodles. 2. Stir fry tofu and veggies. 3. Add noodles and sauce. 4. Top with peanuts.", "health_benefits": "Plant-based protein, gluten-free carbs, and healthy fats."},
        {"meal_type": "breakfast", "country": "Asian", "title": "Congee (Rice Porridge)", "calories": 250, "protein": 8, "carbs": 45, "fat": 4, "diet_type": "Vegan", "ingredients": "Rice, ginger, scallions, soy sauce, sesame oil", "recipe_steps": "1. Boil rice with extra water until broken down. 2. Garnish with ginger and scallions.", "health_benefits": "Very easy to digest, hydrating, and warming."},
        
        {"meal_type": "lunch", "country": "Mediterranean", "title": "Greek Salad with Grilled Chicken", "calories": 400, "protein": 35, "carbs": 15, "fat": 22, "diet_type": "Non-Vegetarian", "ingredients": "Chicken breast, cucumber, tomatoes, olives, feta cheese, olive oil", "recipe_steps": "1. Grill chicken. 2. Chop veggies. 3. Toss with olives, feta, and olive oil dressing.", "health_benefits": "Heart-healthy fats, high protein, and hydrating vegetables."},
        {"meal_type": "dinner", "country": "Mediterranean", "title": "Baked Salmon with Asparagus", "calories": 450, "protein": 40, "carbs": 8, "fat": 25, "diet_type": "Non-Vegetarian", "ingredients": "Salmon fillet, asparagus, lemon, olive oil, garlic", "recipe_steps": "1. Arrange salmon and asparagus on a pan. 2. Drizzle with oil and lemon. 3. Bake until flaky.", "health_benefits": "Rich in Omega-3 fatty acids for brain and heart health."},
        {"meal_type": "snack", "country": "Mediterranean", "title": "Hummus with Pita & Carrots", "calories": 300, "protein": 10, "carbs": 40, "fat": 12, "diet_type": "Vegan", "ingredients": "Chickpeas, tahini, lemon juice, pita bread, carrots", "recipe_steps": "1. Blend chickpeas, tahini, and lemon. 2. Serve with sliced carrots and pita.", "health_benefits": "Great source of plant protein and fiber."}
    ]

    for item in NEW_MEALS:
        mtype = item["meal_type"]
        if mtype not in MEAL_LIBRARY:
            MEAL_LIBRARY[mtype] = []
        
        # Check if exists
        if not any(m["title"] == item["title"] for m in MEAL_LIBRARY[mtype]):
            MEAL_LIBRARY[mtype].append(item)

    # Save back to JSON
    with open(json_path, "w") as f:
        json.dump(MEAL_LIBRARY, f, indent=4)

    # Create food_dataset.csv
    csv_rows = [["item_id", "name", "calories", "protein", "carbs", "fat", "fiber", "diet_type", "meal_type", "goal_tag"]]
    item_id = 1
    for cat, meals in MEAL_LIBRARY.items():
        for m in meals:
            # Determine goal_tag based on calories roughly
            cal = m["calories"]
            if cal < 400: goal = "Weight Loss"
            elif cal > 600: goal = "Muscle Gain"
            else: goal = "Maintenance"
            
            csv_rows.append([
                item_id, m["title"], m["calories"], m["protein"], m["carbs"], m["fat"], 
                m.get("fiber", max(2, m["carbs"] // 10)), m["diet_type"], cat.capitalize(), goal
            ])
            item_id += 1

    csv_path = os.path.join(root_dir, "data", "food_dataset.csv")
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(csv_rows)

    print(f"Total foods created: {item_id - 1}")

if __name__ == "__main__":
    main()
