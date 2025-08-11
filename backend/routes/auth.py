from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import bcrypt
import jwt  # Correct import for PyJWT
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from database import meal_plans_collection as users_collection




# Load environment variables
load_dotenv()

# Ensure SECRET_KEY is loaded
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("SECRET_KEY is not set in the environment variables!")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 100

# Auth Router
auth_router = APIRouter()

# Pydantic Models
class User(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str

# Helper function to create JWT token
def create_jwt_token(data: dict, expires_delta: timedelta = timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)):
    to_encode = data.copy()
    to_encode.update({"exp": datetime.utcnow() + expires_delta})
    
    # Generate JWT token
    try:
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)  # Ensure PyJWT is used correctly
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Token generation failed: {str(e)}")

# **Signup Route**
@auth_router.post("/signup", response_model=dict)
def signup(user: User):
    if not user.username or not user.password:
        raise HTTPException(status_code=400, detail="Username and password cannot be empty")

    if len(user.password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters long")

    existing_user = users_collection.find_one({"username": user.username})
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")

    # Hash password and store as string
    hashed_password = bcrypt.hashpw(user.password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    users_collection.insert_one({"username": user.username, "password": hashed_password})
    return {"message": "User registered successfully"}

# **Login Route**
@auth_router.post("/login", response_model=TokenResponse)
def login(user: User):
    if not user.username or not user.password:
        raise HTTPException(status_code=400, detail="Username and password cannot be empty")

    stored_user = users_collection.find_one({"username": user.username})
    
    if not stored_user:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    stored_password = stored_user["password"]

    # Fix password check issue
    if not bcrypt.checkpw(user.password.encode("utf-8"), stored_password.encode("utf-8")):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    # Generate JWT Token
    token = create_jwt_token({"username": user.username})
    return {"access_token": token, "token_type": "bearer"}
