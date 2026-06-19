"""Quick test of all endpoints."""
import requests
import json

BASE = "http://localhost:5000/api"

# 1. Login
r = requests.post(f"{BASE}/auth/login", json={
    "email": "demo@nutriapp.com",
    "password": "demo123",
})
token = r.json()["token"]
h = {"Authorization": f"Bearer {token}"}
print("Login OK")

# 2. Profile
p = requests.get(f"{BASE}/profile", headers=h)
print("\n=== PROFILE ===")
print(json.dumps(p.json(), indent=2))

# 3. Meals
m = requests.get(f"{BASE}/meals", headers=h)
data = m.json()
print("\n=== MEALS ===")
for key in ["breakfast", "lunch", "dinner", "snack"]:
    items = data.get(key, [])
    print(f"  {key}: {len(items)} items")
    for item in items:
        print(f"    - {item['title']} ({item['calories']} kcal)")

# 4. Check a meal detail has recipe
if data.get("breakfast"):
    meal_id = data["breakfast"][0]["id"]
    d = requests.get(f"{BASE}/meals/{meal_id}", headers=h)
    detail = d.json()
    print(f"\n=== DETAIL: {detail['title']} ===")
    print(f"  Calories: {detail['calories']}")
    print(f"  Protein: {detail['protein']}g")
    print(f"  Carbs: {detail['carbs']}g")
    print(f"  Fat: {detail['fat']}g")
    print(f"  Ingredients: {detail['ingredients'][:80]}...")
    print(f"  Recipe: {detail['recipe_steps'][:80]}...")
    print(f"  Benefits: {detail['health_benefits'][:80]}...")

# 5. Save profile with diet change and refresh
print("\n=== SAVE PROFILE (diet=Non-Veg) ===")
sp = requests.post(f"{BASE}/profile", headers=h, json={
    "name": "Demo User",
    "age": "25",
    "gender": "Male",
    "height_cm": "175",
    "weight_kg": "70",
    "goal": "Muscle Gain",
    "allergy": "None",
    "diet": "Non-Veg",
})
print(f"  Status: {sp.status_code}")
print(f"  Diet saved: {sp.json()['profile']['diet']}")

# 6. Refresh meals with new preferences
print("\n=== REFRESH MEALS (Non-Veg) ===")
rf = requests.post(f"{BASE}/meals/refresh", headers=h)
rdata = rf.json()["meals"]
for key in ["breakfast", "lunch", "dinner", "snack"]:
    items = rdata.get(key, [])
    print(f"  {key}: {[i['title'] for i in items]}")

print("\nAll tests passed!")
