# 🥗 SmartBite — AI-Powered Personalized Diet Planner

SmartBite is a full-stack nutrition and meal-planning application that combines **machine-learning-based food recommendations** with a **Gemini-powered Virtual Doctor chatbot**. It helps users generate a personalized seven-day meal plan using profile information such as age, height, weight, dietary preference, activity level, allergies, nutritional deficiencies, and selected health conditions.

The application includes a React frontend, a FastAPI backend, an XGBoost food-ranking model, MongoDB-backed account storage, and Google Gemini-powered text and image assistance.

> **Health Disclaimer:** SmartBite is an educational and wellness-support application. The Virtual Doctor provides AI-generated informational responses and image-based observations. It is not a licensed medical professional, does not provide a confirmed diagnosis, and must not replace professional medical advice. Do not use it for emergencies.

---

## ✨ Features

### 1. Personalized Seven-Day Meal Planning

- Collects user information including name, age, weight, height, gender, dietary preference, activity level, allergies, nutritional deficiencies, and health conditions.
- Calculates Body Mass Index (BMI).
- Estimates maintenance calories using the Mifflin–St Jeor equation and activity multipliers.
- Uses a pre-trained XGBoost model to score candidate foods against encoded patient and food features.
- Filters food options based on meal type, dietary preference, and excluded ingredients.
- Generates a personalized seven-day meal plan.
- Includes breakfast, lunch, snacks, dinner, estimated serving sizes, calorie information, and seasonal fruit suggestions.

### 2. 🩺 Virtual Doctor Chatbot

SmartBite includes an AI-powered Virtual Doctor chatbot integrated into the landing page.

- Interactive chatbot interface for health-related conversations.
- Uses Google Gemini 2.0 Flash for text-based responses.
- Detects configured health-related keywords such as disease, symptoms, skin issues, infections, and rashes.
- Requests image uploads for certain health-related queries.
- Supports image uploads for AI-assisted image analysis.
- Uses Gemini Vision capabilities to generate observations from uploaded images.
- Formats responses into concise, readable sections.

### 3. 🔐 User Authentication

- User registration and login.
- Password hashing using bcrypt.
- JWT token generation using PyJWT.
- MongoDB-backed user credential storage.
- Frontend authentication context for managing login state.

### 4. 🎨 Interactive Frontend

- React-based user interface.
- Responsive landing page and navigation.
- User registration and login forms.
- Personalized profile form.
- Seven-day meal-plan display.
- Animated components using Framer Motion.
- Interactive chatbot interface.

---

## 🧰 Technology Stack

| Category | Technologies |
|---|---|
| Frontend | React 19, JavaScript, React Router |
| UI & Animation | CSS, Framer Motion, React Icons, React CountUp |
| API Communication | Axios, Fetch API |
| Backend | Python, FastAPI, Uvicorn, Pydantic |
| Machine Learning | XGBoost |
| Data Processing | Pandas, NumPy |
| Generative AI | Google Gemini 2.0 Flash |
| Database | MongoDB, PyMongo |
| Authentication | bcrypt, PyJWT |

---

## 🏗️ System Architecture

```text
                    ┌────────────────────────────┐
                    │       React Frontend       │
                    │                            │
                    │  Landing Page               │
                    │  Signup / Login             │
                    │  Profile Form               │
                    │  Meal Plan Display          │
                    │  Virtual Doctor Chatbot     │
                    └─────────────┬──────────────┘
                                  │
                                  │ HTTP Requests
                                  ▼
                    ┌────────────────────────────┐
                    │       FastAPI Backend      │
                    │                            │
                    │  /auth/signup               │
                    │  /auth/login                │
                    │  /plan                      │
                    │  /chat                      │
                    │  /upload-image              │
                    └────────┬───────────┬───────┘
                             │           │
                   Meal Plan │           │ AI Requests
                             ▼           ▼
                 ┌────────────────┐  ┌─────────────────┐
                 │ Diet Planner   │  │ Google Gemini   │
                 │                │  │                 │
                 │ BMI Calculation│  │ Text Responses  │
                 │ Calorie Est.   │  │ Image Analysis  │
                 │ Food Filtering │  │                 │
                 │ XGBoost Model  │  └─────────────────┘
                 └───────┬────────┘
                         │
                         ▼
                 ┌──────────────────┐
                 │ ML Model & Data  │
                 │                  │
                 │ XGBoost Model    │
                 │ Patient Dataset  │
                 │ Food Dataset     │
                 └──────────────────┘

                 ┌──────────────────┐
                 │ MongoDB          │
                 │                  │
                 │ User Credentials │
                 └──────────────────┘
```

---

## 🔄 Application Workflows

### Meal Plan Generation Workflow

1. User registers or logs into SmartBite.
2. User enters personal and dietary information through the profile form.
3. React sends the profile information to the FastAPI `/plan` endpoint.
4. FastAPI validates the request using Pydantic.
5. The backend calculates BMI and estimated maintenance calories.
6. Patient attributes are encoded into the feature format expected by the XGBoost model.
7. Candidate food items are filtered based on dietary preference, meal type, and exclusions.
8. XGBoost predicts recommendation scores for candidate foods.
9. The system selects high-scoring food options for each meal.
10. Serving sizes and calorie estimates are calculated.
11. A seven-day meal plan is returned to the frontend.
12. React displays the personalized meal plan.

### Virtual Doctor Workflow

1. User opens the Virtual Doctor chatbot from the landing page.
2. The chatbot retrieves an initial greeting from the backend.
3. User submits a text message.
4. The message is sent to the FastAPI `/chat` endpoint.
5. The backend checks configured health-related keywords.
6. For matching keywords, the chatbot requests an image upload.
7. User uploads an image through the chatbot interface.
8. The image is sent to the `/upload-image` endpoint.
9. Gemini processes the image and generates AI-assisted observations.
10. The backend formats the response and returns it to the chatbot.

---

## 📁 Project Structure

```text
SmartBite-Ai-Powered-Diet-Planner/
│
├── backend/
│   ├── main.py
│   ├── diet_planner.py
│   ├── constants.py
│   ├── database.py
│   ├── dependencies.py
│   ├── requirements.txt
│   ├── Pipfile
│   │
│   ├── routes/
│   │   └── auth.py
│   │
│   └── processed_data/
│       ├── xgboost_patient_food_model.json
│       ├── processed_patients.pkl
│       └── processed_foods.pkl
│
├── frontend/
│   ├── public/
│   │   ├── images/
│   │   └── index.html
│   │
│   └── src/
│       ├── App.js
│       ├── App.css
│       ├── index.js
│       │
│       ├── components/
│       │   ├── LandingPage.js
│       │   ├── Navbar.js
│       │   ├── Signup.js
│       │   ├── Login.js
│       │   ├── ProfileForm.js
│       │   ├── MealDisplay.js
│       │   └── ChatBot.js
│       │
│       ├── context/
│       │   └── AuthContext.js
│       │
│       └── styles/
│
├── package.json
├── package-lock.json
└── README.md
```

---

## ⚙️ Getting Started

### Prerequisites

Make sure you have the following installed:

- Python 3.10 or compatible version
- Node.js and npm
- MongoDB (local or cloud instance)
- Google Gemini API key
- Git

### 1. Clone the Repository

```bash
git clone https://github.com/SubhankarPani/SmartBite-Ai-Powered-Diet-Planner.git

cd SmartBite-Ai-Powered-Diet-Planner
```

### 2. Backend Setup

Navigate to the backend directory:

```bash
cd backend
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate the environment.

**Windows PowerShell:**

```powershell
.venv\Scripts\Activate.ps1
```

**Linux / macOS:**

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Install additional packages used by the application if they are not already installed:

```bash
python -m pip install google-generativeai pymongo bcrypt PyJWT python-dotenv python-multipart
```

### 3. Environment Configuration

Create a `.env` file inside the backend directory:

```env
GEMINI_API_KEY=your_google_gemini_api_key

MONGO_URI=your_mongodb_connection_string

MONGO_DB_NAME=your_database_name

SECRET_KEY=your_jwt_secret_key
```

Replace the placeholder values with your own credentials.

### 4. Run the Backend

From the backend directory:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Backend API:

```text
http://localhost:8000
```

FastAPI Swagger documentation:

```text
http://localhost:8000/docs
```

### 5. Frontend Setup

Open a new terminal and navigate to the frontend directory:

```bash
cd frontend
```

Install dependencies:

```bash
npm install
```

Start the React application:

```bash
npm start
```

Frontend:

```text
http://localhost:3000
```

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Backend welcome message |
| POST | `/auth/signup` | Register a new user |
| POST | `/auth/login` | Authenticate user and generate JWT |
| POST | `/plan` | Generate personalized seven-day meal plan |
| GET | `/chat` | Get chatbot welcome message |
| POST | `/chat` | Send a message to the Virtual Doctor |
| POST | `/upload-image` | Upload an image for Gemini analysis |

### Example Meal Plan Request

```json
{
  "patient_name": "Alex",
  "age": 28,
  "weight": 72,
  "height": 175,
  "gender": "male",
  "diet_pref": "veg",
  "activity": "moderate",
  "allergies": ["peanuts"],
  "deficiencies": ["vitamin d"],
  "diseases": [],
  "exceptions": "mushrooms; very spicy food"
}
```

### Example Chat Request

```json
{
  "message": "Can you suggest some healthy breakfast options?"
}
```

### Image Upload

The `/upload-image` endpoint accepts a multipart/form-data request with the image supplied under the field name `file`.

---

## 🧠 Machine Learning Implementation

SmartBite uses an XGBoost Booster model to score food recommendations based on user and food characteristics.

### Input Features

The recommendation pipeline uses information such as:

- Age
- Weight
- Height
- BMI
- BMI category
- Gender
- Dietary preference
- Activity level
- Allergies
- Nutritional deficiencies
- Health conditions
- Food calories
- Food protein
- Food fat
- Food carbohydrates

### Recommendation Pipeline

1. Calculate BMI from user height and weight.
2. Estimate daily maintenance calories using the Mifflin–St Jeor formula.
3. Encode patient information into model-compatible features.
4. Filter food items by meal type and dietary restrictions.
5. Combine patient features with food nutritional attributes.
6. Align the input data with the model's expected feature names.
7. Generate prediction scores using XGBoost.
8. Rank candidate foods by score.
9. Select up to seven recommendations for each meal category.
10. Estimate serving sizes based on calorie allocation.

### Calorie Distribution

The current implementation uses the following default distribution:

| Meal | Calorie Allocation |
|---|---:|
| Breakfast | 35% |
| Lunch | 30% |
| Snack | 10% |
| Dinner | 25% |

Serving sizes are estimated from food calorie values and constrained to a configured range of 30–500 grams.

---

## 🔐 Security and Implementation Notes

- Passwords are hashed using bcrypt.
- JWT tokens are generated using PyJWT.
- MongoDB stores account credentials.
- API keys and database credentials are configured through environment variables.

Some implementation areas remain prototype-level and should be strengthened before production deployment, particularly JWT validation, CORS restrictions, upload validation, and API URL configuration.

---

## 🚀 Future Enhancements

- Improve JWT authentication and route-level authorization.
- Add meal-plan history and user-specific saved plans.
- Add meal-plan regeneration and customization.
- Improve nutritional recommendation constraints.
- Add model evaluation and recommendation-quality metrics.
- Add more advanced Virtual Doctor conversation capabilities.
- Improve image upload validation and medical safety guardrails.
- Add workout recommendations based on fitness goals.
- Add a personalized pet diet planning module.
- Improve deployment configuration and automated testing.

---

## 🤝 Contributing

Contributions are welcome!

1. Fork the repository.
2. Create a feature branch.
3. Commit your changes.
4. Push the branch.
5. Open a Pull Request.

---

## 📄 License

No license file is currently included in this repository.

---

## 👨‍💻 Author

**Subhankar Pani**

GitHub: [@SubhankarPani](https://github.com/SubhankarPani)

Project: [SmartBite — AI-Powered Diet Planner](https://github.com/SubhankarPani/SmartBite-Ai-Powered-Diet-Planner)

## 📊 Model Performance

The XGBoost classification model was evaluated on a test dataset containing **72,000 samples**.

### Classification Report

| Metric | Class 0 | Class 1 |
|---|---:|---:|
| Precision | 0.88 | 0.95 |
| Recall | 0.99 | 0.43 |
| F1-Score | 0.94 | 0.59 |
| Support | 58,526 | 13,474 |

**Overall Performance:**
- Accuracy: **89%**
- Macro F1-Score: **0.76**
- Weighted F1-Score: **0.87**
- Test Samples: **72,000**

### Confusion Matrix

```text
[[58194   332]
 [ 7744  5730]]
```

## 🥗 Sample 7-Day Meal Plan Output

**Patient Profile:**
- Patient: Subhankar Pani
- BMI: 28.69 (Overweight)
- Maintenance Calories: 2,671 kcal/day

**Sample Meal Recommendations**

| Day | Meal | Recommended Food | Quantity | Calories |
|---|---|---|---:|---:|
| Day 1 | Breakfast | Spinach Soup | 167g | 936 kcal |
| Day 1 | Lunch | Sattu Drink | 175g | 802 kcal |
| Day 1 | Snack | Rajma Chawal | 48g | 268 kcal |
| Day 1 | Dinner | Karela Sabzi | 127g | 668 kcal |
| Day 2 | Breakfast | Paneer Tikka | 197g | 936 kcal |
| Day 2 | Lunch | Cauliflower Curry with Roti | 363g | 802 kcal |
| Day 2 | Snack | Pav Bhaji | 69g | 268 kcal |
| Day 2 | Dinner | Kadhi Bari | 304g | 668 kcal |

**Daily Calorie Summary:**
- Day 1: 2,674 kcal
- Day 2: 2,674 kcal
- Day 3: 2,674 kcal
- Day 7: 2,682 kcal

*The application generates four meals per day across a personalized seven-day meal plan.*

## 🧾 Supported Personalization Categories

**Food Allergies:** Eggs, Gluten, Lactose (Dairy), Peanuts, Shellfish, Soy, Tree Nuts.

**Nutritional Deficiencies:** Calcium, Folate (Vitamin B9), Iron, Magnesium, Protein, Vitamin B12, Vitamin D, Zinc.

**Medical Conditions:** Diabetes, Fatty Liver, Gastritis, Heart Disease, High Cholesterol, Hypertension, Hypothyroidism, Kidney Disease, Obesity, PCOS/PCOD.
