import json
import pandas as pd
import xgboost as xgb
from collections import defaultdict
from datetime import datetime
import random
import re
from constants import SEASONAL_FRUITS  # Make sure this file has the dict for seasonal fruits

MODEL_PATH     = "processed_data/xgboost_patient_food_model.json"
PATIENTS_PATH  = "processed_data/processed_patients.pkl"
FOODS_PATH     = "processed_data/processed_foods.pkl"

# Load model JSON to get feature names
with open(MODEL_PATH, "r") as f:
    model_json = json.load(f)
feature_names = model_json["learner"]["feature_names"]

# Load the trained XGBoost model
_model = xgb.Booster()
_model.load_model(MODEL_PATH)

# Load foods and patients datasets
_foods = pd.read_pickle(FOODS_PATH)
_patients = pd.read_pickle(PATIENTS_PATH)


def encode_patient_row(age, weight, height, gender, allergies, deficiencies, diseases, diet_pref, activity):
    bmi = weight / ((height / 100) ** 2)
    encoded = {"age": age, "weight": weight, "height": height, "bmi": bmi}

    # One-hot encode BMI categories
    encoded["bmi_category_Underweight"] = int(bmi < 18.5)
    encoded["bmi_category_Normal"] = int(18.5 <= bmi < 25)
    encoded["bmi_category_Overweight"] = int(25 <= bmi < 30)
    encoded["bmi_category_Obese"] = int(bmi >= 30)

    for col in _patients.columns:
        if col.startswith("gender_"):
            encoded[col] = int(col == f"gender_{gender}")
        if col.startswith("diet_preference_"):
            encoded[col] = int(col == f"diet_preference_{diet_pref}")
        if col.startswith("activity_level_"):
            encoded[col] = int(col == f"activity_level_{activity}")
        if col.startswith("allergies_"):
            encoded[col] = int(col.replace("allergies_", "") in allergies)
        if col.startswith("deficiencies_"):
            encoded[col] = int(col.replace("deficiencies_", "") in deficiencies)
        if col.startswith("diseases_"):
            encoded[col] = int(col.replace("diseases_", "") in diseases)

    # Ensure all features exist in encoded
    for feat in _patients.columns:
        encoded.setdefault(feat, 0)

    return pd.Series(encoded)


def estimate_maintenance_calories(age, weight, height, gender, activity):
    # Mifflin-St Jeor formula
    if gender.lower() == "male":
        bmr = 10 * weight + 6.25 * height - 5 * age + 5
    else:
        bmr = 10 * weight + 6.25 * height - 5 * age - 161

    activity_factors = {
        "sedentary": 1.2,
        "light": 1.375,
        "moderate": 1.55,
        "active": 1.725,
        "veryactive": 1.9
    }
    return int(bmr * activity_factors.get(activity.lower(), 1.55))


def matches_exceptions(text, exceptions):
    for exc in exceptions:
        if re.search(rf"\b{re.escape(exc)}\b", text, flags=re.IGNORECASE):
            return True
    return False


def generate_meal_plan_from_inputs(
    patient_name: str,
    age: int,
    weight: float,
    height: float,
    gender: str,
    allergies: list[str] | str,
    deficiencies: list[str] | str,
    diseases: list[str] | str,
    diet_pref: str,
    activity: str,
    exceptions: str = "",
    meals_per_day: list[str] | None = None,
    calorie_split: dict = None
) -> dict:
    if meals_per_day is None:
        meals_per_day = ["breakfast", "lunch", "snack", "dinner"]

    if calorie_split is None:
        calorie_split = {
            "breakfast": 0.35,
            "lunch": 0.30,
            "snack": 0.10,
            "dinner": 0.25
        }

    # Parse string inputs to lists if needed
    if isinstance(allergies, str):
        allergies = [a.strip().lower() for a in allergies.split(";") if a.strip()]
    if isinstance(deficiencies, str):
        deficiencies = [d.strip().lower() for d in deficiencies.split(";") if d.strip()]
    if isinstance(diseases, str):
        diseases = [d.strip().lower() for d in diseases.split(";") if d.strip()]
    exceptions_list = [e.strip().lower() for e in exceptions.split(";") if e.strip()]

    # Encode patient data
    patient = encode_patient_row(age, weight, height, gender, allergies, deficiencies, diseases, diet_pref, activity)
    maintenance = estimate_maintenance_calories(age, weight, height, gender, activity)
    meals_per_day = [m.lower().strip() for m in meals_per_day]

    rows = []
    food_lookup = defaultdict(dict)

    for _, food in _foods.iterrows():
        meal_type = food["meal_type"].lower().strip()
        if meal_type not in meals_per_day:
            continue

        name = str(food["name"]).lower()
        ingredients = str(food.get("ingredients", "")).lower()
        dtype_val = food.get("diet_Type")
        diet_type = (
            dtype_val[0].lower() if isinstance(dtype_val, list) and dtype_val
            else dtype_val.lower() if isinstance(dtype_val, str)
            else ""
        )

        # Skip foods matching any exceptions (name, ingredients, or diet type)
        if matches_exceptions(name, exceptions_list) or matches_exceptions(ingredients, exceptions_list) or matches_exceptions(diet_type, exceptions_list):
            continue

        # Filter based on diet preference
        if diet_pref.lower() == "veg" and diet_type == "non-veg":
            continue
        if diet_pref.lower() == "vegan" and diet_type in ["non-veg", "veg"]:
            continue

        base = {
            "age": patient["age"],
            "weight": patient["weight"],
            "height": patient["height"],
            "bmi": patient["bmi"],
            "food_calories": food["calories"],
            "food_protein": food["protein"],
            "food_fat": food["fat"],
            "food_carbs": food["carbs"]
        }
        for col in patient.index:
            base[col] = patient[col]

        food_lookup[meal_type][food["name"]] = food
        rows.append((food["name"], meal_type, base))

    if not rows:
        # Return simple response with empty meal plan if no foods matched
        return {
            "patient_name": patient_name,
            "BMI": patient["bmi"],
            "maintenance_calories": maintenance,
            "meal_plan": []
        }

    df = pd.DataFrame([r[2] for r in rows])

    # Add missing features with zeros
    for feat in feature_names:
        if feat not in df.columns:
            df[feat] = 0

    df = df[feature_names]
    dmat = xgb.DMatrix(df, feature_names=feature_names)
    preds = _model.predict(dmat)

    raw_by_meal = defaultdict(list)
    for (name, mtype, _), score in zip(rows, preds):
        raw_by_meal[mtype].append((name, float(score)))

    meal_plan = {}
    for m in meals_per_day:
        candidates = raw_by_meal.get(m, [])
        above = [x for x in candidates if x[1] > 0.5]
        fallback = sorted(candidates, key=lambda x: x[1], reverse=True)[:7] if candidates else [("No suitable option", 0.0)]
        meal_plan[m] = sorted(above, key=lambda x: x[1], reverse=True)[:7] if above else fallback

    final = {m: [name for name, _ in meal_plan[m]] for m in meals_per_day}

    structured_plan = []
    current_month = datetime.now().strftime("%B")

    for i in range(7):
        day_plan = {}
        total_calories = 0

        for meal in meals_per_day:
            food_name = final[meal][i] if i < len(final[meal]) else "No suitable option"
            food_row = food_lookup[meal].get(food_name)

            if food_row is not None and food_row["calories"] > 0:
                meal_target_cals = maintenance * calorie_split.get(meal, 0)
                serving_g = round((meal_target_cals / food_row["calories"]) * 100)
                # Clamp serving size
                serving_g = max(30, min(serving_g, 500))
                calories_served = round(food_row["calories"] * (serving_g / 100))

                day_plan[meal] = {
                    "name": food_name.title(),
                    "serving_g": serving_g,
                    "calories": calories_served
                }
                total_calories += calories_served
            else:
                day_plan[meal] = {
                    "name": "No suitable option",
                    "serving_g": 0,
                    "calories": 0
                }

        seasonal_fruits = SEASONAL_FRUITS.get(current_month, [])
        fruit = random.choice(seasonal_fruits) if seasonal_fruits else "No seasonal fruit available"
        day_plan["fruit"] = fruit

        day_plan["total_calories"] = total_calories
        structured_plan.append(day_plan)

    # Return clean JSON without notes or formatted strings
    return {
        "patient_name": patient_name,
        "BMI": patient["bmi"],
        "maintenance_calories": maintenance,
        "meal_plan": structured_plan
    }
