# 🥗 SmartBite — AI-Powered Personalized Diet Planner

SmartBite is a full-stack nutrition and meal-planning application that combines **machine-learning-based food recommendations** with a **Gemini-powered Virtual Doctor chatbot**. It helps users generate a personalized seven-day meal plan using profile information such as age, height, weight, dietary preference, activity level, allergies, nutritional deficiencies, and selected health conditions.

The application includes a React frontend, a FastAPI backend, an XGBoost food-ranking model, MongoDB-backed account storage, and Google Gemini-powered text and image assistance.

> **Health disclaimer:** SmartBite is an educational and wellness-support application. The Virtual Doctor provides AI-generated informational responses and image-based observations; it is not a licensed medical professional, does not provide a confirmed diagnosis, and must not replace professional medical advice. Do not use it for emergencies.

---

## ✨ Features

### 1. Personalized seven-day meal planning
- Collects a user profile containing name, age, weight, height, gender, diet preference, activity level, allergies, nutritional deficiencies, health conditions, and food exceptions.
- Calculates Body Mass Index (BMI).
- Estimates maintenance calories using the Mifflin–St Jeor equation and an activity multiplier.
- Uses a pre-trained XGBoost Booster to score candidate foods against the encoded patient and food features.
- Filters candidates by meal type, diet preference, and excluded ingredients or food types.
- Produces a seven-day plan with breakfast, lunch, snack, dinner, portion estimates, calorie estimates, and a seasonal fruit suggestion.

### 2. 🩺 Virtual Doctor chatbot
The landing page includes a floating chat widget labelled **Virtual Doctor**.

- Greets users and accepts text questions.
- Sends general chat messages to Google Gemini 2.0 Flash.
- Checks messages for configured health-related keywords (including disease, symptom, health issue, skin, infection, and rash).
- For messages matching those keywords, asks the user to upload an image.
- Accepts an image upload and sends it to Gemini for AI-assisted image observations.
- Formats the generated response into concise text/bullet-style sections where possible.

**Important implementation note:** The current health-keyword check is a simple keyword-based routing rule. It is not a medical triage system. Image interpretation is model-generated and has not been established as clinically validated.

### 3. Account registration and login
- Signup and login endpoints are provided by FastAPI.
- Passwords are hashed using bcrypt before storage.
- Login verifies the submitted password and issues a JWT signed with HS256.
- The React frontend stores the returned token in browser local storage.

**Current limitation:** The repository's `get_current_user` dependency is a placeholder that returns a fixed test user after checking that a token exists. It does not decode or validate the JWT. Treat the authentication flow as a prototype, not production-grade access control.

### 4. Responsive, animated frontend
- React-based landing page and navigation.
- Signup and login forms.
- Profile form for meal-plan inputs.
- Seven-day meal-plan display.
- Animated UI elements using Framer Motion.
- Charts and visualization libraries are included in the frontend dependencies.

---

## 🧰 Technology Stack

| Layer | Technologies |
|---|---|
| Frontend | React 19, JavaScript, React Router |
| UI and animation | CSS, Framer Motion, React Icons, React CountUp |
| HTTP communication | Axios, Fetch API |
| Backend API | Python, FastAPI, Uvicorn, Pydantic |
| Machine learning | XGBoost |
| Data processing | Pandas, NumPy |
| Generative AI | Google Gemini 2.0 Flash through `google-generativeai` |
| Database | MongoDB, PyMongo |
| Authentication | bcrypt, PyJWT (HS256) |

---

## 🏗️ High-Level Architecture

```text
                         ┌────────────────────────────┐
                         │       React Frontend       │
                         │                            │
                         │  Landing Page / Navbar     │
                         │  Signup / Login            │
                         │  Profile Form              │
                         │  Meal Plan Display         │
                         │  Virtual Doctor Chatbot    │
                         └─────────────┬──────────────┘
                                       │ HTTP requests
                                       ▼
                         ┌────────────────────────────┐
                         │       FastAPI Backend      │
                         │                            │
                         │  /auth/signup               │
                         │  /auth/login                │
                         │  /plan                      │
                         │  /chat                      │
                         │  /upload-image              │
                         └───────┬────────────┬───────┘
                                 │            │
                    Meal planning│            │AI text / image
                                 ▼            ▼
                    ┌──────────────────┐  ┌───────────────────┐
                    │ Diet Planner     │  │ Google Gemini     │
                    │                  │  │ 2.0 Flash         │
                    │ Profile encoding │  │                   │
                    │ BMI / calories   │  │ Text responses    │
                    │ Food filtering   │  │ Image observations│
                    │ XGBoost scoring  │  └───────────────────┘
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │ Local model/data │
                    │                  │
                    │ XGBoost model    │
                    │ Patient features │
                    │ Food dataset     │
                    └──────────────────┘

                    ┌──────────────────┐
                    │ MongoDB          │
                    │                  │
                    │ User credentials │
                    └──────────────────┘
```

---

## 🔄 Application Workflows

### Meal-plan generation
1. A user signs up or logs in.
2. The user opens the profile form and supplies their personal and dietary information.
3. The frontend sends a JSON payload to `POST /plan`.
4. FastAPI validates the payload with a Pydantic model.
5. The diet planner calculates BMI and estimated maintenance calories.
6. Patient attributes are encoded to match the model's expected feature columns.
7. Candidate foods are filtered by meal type, exclusions, and dietary preference.
8. An XGBoost Booster scores the remaining patient-food feature rows.
9. The planner selects high-scoring foods (with a top-ranked fallback when no candidate crosses the configured score threshold).
10. The backend assembles seven days of meals, portion estimates, calorie estimates, and seasonal fruit suggestions.
11. The frontend displays the generated plan.

### Virtual Doctor chat and image upload
1. The chatbot requests an initial greeting from `GET /chat`.
2. The user sends a message to `POST /chat`.
3. The backend checks the message for a small configured list of health-related keywords.
4. For a matching message, the backend responds with a request to upload an image; the frontend switches to its image-upload control.
5. The frontend sends the selected image as multipart form data to `POST /upload-image`.
6. The backend passes the image and a short analysis instruction to Gemini 2.0 Flash.
7. The response is formatted and returned to the chat interface.

---

## 📁 Repository Structure

The following is a simplified view of the main application files:

```text
SmartBite-Ai-Powered-Diet-Planner/
│
├── backend/
│   ├── main.py                       # FastAPI app and API endpoints
│   ├── diet_planner.py               # BMI, calorie estimation and XGBoost recommendations
│   ├── constants.py                  # Seasonal fruit configuration
│   ├── database.py                   # MongoDB connection and collection
│   ├── dependencies.py               # Authentication dependency (currently placeholder)
│   ├── requirements.txt              # Backend Python dependencies
│   ├── Pipfile                       # Pipenv configuration
│   ├── routes/
│   │   └── auth.py                   # Signup and login endpoints
│   └── processed_data/
│       ├── xgboost_patient_food_model.json
│       ├── processed_patients.pkl
│       └── processed_foods.pkl
│
├── frontend/
│   ├── public/
│   │   ├── images/                   # Landing-page and feature images
│   │   └── index.html
│   └── src/
│       ├── App.js                    # React routes and application state
│       ├── components/
│       │   ├── LandingPage.js
│       │   ├── Navbar.js
│       │   ├── Signup.js
│       │   ├── Login.js
│       │   ├── ProfileForm.js
│       │   ├── MealDisplay.js
│       │   └── ChatBot.js            # Virtual Doctor chat interface
│       ├── context/
│       │   └── AuthContext.js
│       └── styles/                   # Component stylesheets
│
├── package.json
├── package-lock.json
└── README.md
```

---

## ⚙️ Getting Started

### Prerequisites
- Python 3.10 or a compatible Python version.
- Node.js and npm.
- A MongoDB database (local or hosted).
- A Google AI Studio API key with access to Gemini 2.0 Flash.
- Git.

### 1. Clone the repository

```bash
git clone https://github.com/SubhankarPani/SmartBite-Ai-Powered-Diet-Planner.git
cd SmartBite-Ai-Powered-Diet-Planner
```

### 2. Configure the backend

```bash
cd backend
python -m venv .venv
```

Activate the environment:

**Windows PowerShell**
```powershell
.venv\Scripts\Activate.ps1
```

**macOS / Linux**
```bash
source .venv/bin/activate
```

Install the packages listed in the backend requirements file:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

The current `backend/requirements.txt` lists FastAPI, Uvicorn, Pandas, XGBoost, and NumPy. The application also imports additional packages, including Google Generative AI, PyMongo, bcrypt, PyJWT, and python-dotenv. Install these if they are not already present:

```bash
python -m pip install google-generativeai pymongo bcrypt PyJWT python-dotenv python-multipart
```

Create a backend environment file named `.env`:

```env
GEMINI_API_KEY=your_google_gemini_api_key
MONGO_URI=your_mongodb_connection_string
MONGO_DB_NAME=your_database_name
SECRET_KEY=replace_with_a_long_random_secret
```

Do not commit real API keys, database credentials, or signing secrets.

### 3. Start the backend

From the `backend` directory:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:

- API root: http://localhost:8000/
- Interactive Swagger documentation: http://localhost:8000/docs

### 4. Configure and start the frontend

Open a second terminal:

```bash
cd frontend
npm install
npm start
```

The React development server normally starts at:

http://localhost:3000

**API URL note:** The current frontend source contains hardcoded `http://localhost:8000` URLs in the chatbot, profile form, and authentication context. Run the backend on that address for the current code, or update the frontend to use a configurable environment-based API base URL before deployment.

---

## 🔌 API Endpoints

The following endpoints are defined in the current FastAPI application.

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/` | Basic API welcome response |
| POST | `/auth/signup` | Register a user |
| POST | `/auth/login` | Verify credentials and return a JWT |
| POST | `/plan` | Generate a personalized seven-day meal plan |
| GET | `/chat` | Return a chatbot greeting |
| POST | `/chat` | Send a text message to the chatbot |
| POST | `/upload-image` | Submit an image for Gemini-assisted analysis |

### Example meal-plan request

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

### Example chatbot request

```json
{
  "message": "Can you suggest some general healthy breakfast ideas?"
}
```

### Image upload
Send a multipart/form-data request to `/upload-image` with the image in a form field named `file`.

---

## 🧠 Machine Learning Recommendation Logic

The meal planner loads the XGBoost model from:

`backend/processed_data/xgboost_patient_food_model.json`

It also reads the processed food and patient feature data from the two pickle files in the same directory.

At inference time, the application:
- Computes BMI from height and weight.
- Encodes BMI category, gender, diet preference, activity, allergies, deficiencies, and diseases.
- Combines the patient features with food nutrition fields such as calories, protein, fat, and carbohydrates.
- Aligns the input DataFrame with the feature names stored in the model.
- Creates an XGBoost `DMatrix` and obtains prediction scores.
- Ranks candidate foods within each meal category and selects up to seven options.
- Estimates serving size from the meal's calorie allocation and the food's calories per 100 grams, with a configured range of 30–500 grams.

The current source contains model inference and model/data artifacts. It does not include a model-training script or documented evaluation metrics. Therefore, this README does not claim a particular training process, accuracy, or clinical nutrition validation.

---

## 🔐 Security and Deployment Notes

Before using this project beyond local development, address the following items:

1. **Remove committed environment files.** The repository currently contains `backend/.env` and `frontend/.env`. Remove them from version control, add appropriate ignore rules, and rotate any credentials that may have been stored in them. Revoke and replace exposed API keys, MongoDB credentials, and JWT secrets.
2. **Validate JWTs correctly.** Replace the placeholder `get_current_user` implementation with signature, expiry, and user validation. Protect routes that require authentication.
3. **Restrict CORS.** The current backend allows all origins. Configure an explicit list of trusted frontend origins.
4. **Externalize API URLs.** Replace hardcoded localhost URLs with environment-based configuration.
5. **Validate image uploads.** Add file-size limits, content-type checks, and safe error handling.
6. **Add medical safety boundaries.** Clearly communicate the limitations of AI-generated health responses and direct users to qualified professionals for diagnosis or treatment.
7. **Review database design.** The current authentication code uses the `meal_plans` collection for user records. Separate collections and persistence responsibilities before expanding the application.
8. **Review repository hygiene.** Remove generated `__pycache__` files and avoid committing local build artifacts or secrets.

---

## 🚀 Future Improvements

Potential next steps for the project include:

- Move all frontend API URLs into a single configurable API client.
- Complete JWT authentication and authorization.
- Persist generated meal plans and associate them with authenticated users.
- Add meal-plan history, editing, and regeneration.
- Add stronger validation for nutritional constraints and allergies.
- Add automated unit and integration tests for API and recommendation logic.
- Track model versioning and evaluate recommendations on a held-out dataset.
- Add explicit privacy, consent, retention, and deletion controls for profile and uploaded image data.
- Replace the deprecated `google-generativeai` integration with the current supported Google GenAI SDK after compatibility testing.
- Add safer, medically reviewed response boundaries to the Virtual Doctor experience.

---

## 🤝 Contributing

1. Fork the repository.
2. Create a feature branch: `git checkout -b feature/your-feature`.
3. Commit your changes: `git commit -m "Add your feature"`.
4. Push the branch: `git push origin feature/your-feature`.
5. Open a pull request describing the change and how it was tested.

---

## 📄 License

No license file was identified in the repository when this README was prepared. Until a license is added, assume that the repository's code is not licensed for reuse, redistribution, or modification by others.

---

## 👨‍💻 Author

**Subhankar Pani**

GitHub: [@SubhankarPani](https://github.com/SubhankarPani)

Repository: [SmartBite — AI-Powered Diet Planner](https://github.com/SubhankarPani/SmartBite-Ai-Powered-Diet-Planner)
