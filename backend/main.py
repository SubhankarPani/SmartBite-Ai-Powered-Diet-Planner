import os
import base64
from typing import List, Optional
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from routes.auth import auth_router
from diet_planner import generate_meal_plan_from_inputs
import google.generativeai as genai
from dotenv import load_dotenv
import re

# Load .env variables
load_dotenv()

# -----------------------
# Setup FastAPI app
# -----------------------

app = FastAPI(title="Diet Planner API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (change this in production)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Diet Planner API"}

app.include_router(auth_router, prefix="/auth")

# -----------------------
# Setup Gemini
# -----------------------

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

chat_model = genai.GenerativeModel(model_name="models/gemini-2.0-flash")
vision_model = genai.GenerativeModel(model_name="models/gemini-2.0-flash")

# -----------------------
# Helper function to clean and format medical image analysis text concisely
# -----------------------

def clean_and_concise(text: str) -> str:
    """
    Convert any long text into concise bullet points with a blank line after each.
    Handles Observations and Home Remedy sections explicitly if present.
    """

    # Normalize spaces and strip
    text = re.sub(r"\s+", " ", text).strip()

    # Attempt to find sections explicitly
    sections = {}
    section_titles = ["observations", "home remedy", "home remedies"]

    # Regex pattern to extract sections by titles
    pattern = re.compile(
        r"(?P<title>observations|home remedy|home remedies)[:\-]?\s*(?P<content>.*?)(?=(observations|home remedy|home remedies|$))",
        re.IGNORECASE | re.DOTALL,
    )

    for match in pattern.finditer(text):
        title = match.group("title").capitalize()
        content = match.group("content").strip()
        sections[title] = content

    # If no specific sections found, treat entire text as 'Observations'
    if not sections:
        sections["Observations"] = text

    def to_bullets(section_text: str) -> str:
        # Split by sentences, semicolons, or numbered lists for brevity
        points = re.split(r"\s*(?:\.|;|\n|\d+\.)\s*", section_text)
        points = [p.strip(" -") for p in points if p.strip()]
        return "\n\n".join(f"- {p}" for p in points)

    # Format each section concisely
    formatted_sections = []
    for title in section_titles:
        if title.capitalize() in sections:
            formatted_sections.append(
                f"{title.capitalize()}:\n\n{to_bullets(sections[title.capitalize()])}"
            )

    return "\n\n".join(formatted_sections).strip()

# -----------------------
# Chat + Image Upload
# -----------------------

class ChatRequest(BaseModel):
    message: str

@app.get("/chat")
def welcome_chat():
    return {"response": "Hello, how can I help you?"}

@app.post("/chat")
async def chat(request: ChatRequest):
    query = request.message.lower()

    if any(keyword in query for keyword in ["disease", "symptom", "health issue", "skin", "infection", "rash"]):
        return {"response": "Please upload an image for better diagnosis."}

    response = chat_model.generate_content(query)
    cleaned = clean_and_concise(response.text)
    return {"response": cleaned}

@app.post("/upload-image")
async def upload_image(file: UploadFile = File(...)):
    contents = await file.read()
    image_bytes = contents

    response = vision_model.generate_content([
        "Please analyze this medical image and provide concise insights:",
        {
            "mime_type": file.content_type,
            "data": image_bytes
        }
    ])

    cleaned_response = clean_and_concise(response.text)
    return {"response": cleaned_response}

# -----------------------
# ML-based Diet Plan Route
# -----------------------

class PlanRequest(BaseModel):
    patient_name: str
    age: int
    weight: float
    height: float
    gender: str
    diet_pref: str
    activity: str
    allergies: List[str] = []
    deficiencies: List[str] = []
    diseases: List[str] = []
    exceptions: Optional[str] = ""
    meals_per_day: Optional[List[str]] = Field(default=["breakfast", "lunch", "snack", "dinner"], exclude=True)

@app.post("/plan")
async def plan(req: PlanRequest):
    return generate_meal_plan_from_inputs(
        patient_name=req.patient_name,
        age=req.age,
        weight=req.weight,
        height=req.height,
        gender=req.gender,
        allergies=req.allergies,
        deficiencies=req.deficiencies,
        diseases=req.diseases,
        diet_pref=req.diet_pref,
        activity=req.activity,
        exceptions=req.exceptions,
        meals_per_day=req.meals_per_day
    )

# -----------------------
# Run the App
# -----------------------

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
