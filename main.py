from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
import os
from typing import Optional
import uvicorn

# Simple models for basic functionality
class SignupRequest(BaseModel):
    email: str
    password: str
    full_name: Optional[str] = None

class LoginRequest(BaseModel):
    email: str
    password: str

class UserResponse(BaseModel):
    id: str
    email: str
    message: str

# Create FastAPI app
app = FastAPI(
    title="AI Script Strategist API",
    version="1.0.0",
    description="Simple backend for AI Script Strategist"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Basic routes
@app.get("/")
async def root():
    return {
        "message": "AI Script Strategist API", 
        "version": "1.0.0", 
        "status": "running",
        "environment_check": {
            "supabase_url": "✅" if os.getenv("SUPABASE_URL") else "❌",
            "supabase_key": "✅" if os.getenv("SUPABASE_KEY") else "❌",
            "jwt_secret": "✅" if os.getenv("JWT_SECRET_KEY") else "❌"
        }
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "AI Script Strategist API"}

# Simple auth endpoints (mock for now)
@app.post("/api/v1/auth/signup", response_model=UserResponse)
async def signup(request: SignupRequest):
    """Simple signup endpoint - returns success for any valid email"""
    try:
        # Basic validation
        if not request.email or "@" not in request.email:
            raise HTTPException(status_code=400, detail="Invalid email format")
        
        if not request.password or len(request.password) < 6:
            raise HTTPException(status_code=400, detail="Password must be at least 6 characters")
        
        # Mock successful signup
        return UserResponse(
            id="user_123",
            email=request.email,
            message="User registered successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/v1/auth/login", response_model=UserResponse)
async def login(request: LoginRequest):
    """Simple login endpoint - returns success for any valid credentials"""
    try:
        # Basic validation
        if not request.email or "@" not in request.email:
            raise HTTPException(status_code=400, detail="Invalid email format")
        
        if not request.password:
            raise HTTPException(status_code=400, detail="Password is required")
        
        # Mock successful login
        return UserResponse(
            id="user_123",
            email=request.email,
            message="Login successful"
        )
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid credentials")

@app.get("/api/v1/scripts")
async def get_scripts():
    """Simple scripts endpoint"""
    return {
        "scripts": [],
        "message": "Scripts endpoint working",
        "total": 0
    }

@app.get("/api/v1/test")
async def test_endpoint():
    """Test endpoint to verify API is working"""
    return {
        "status": "success",
        "message": "API is working correctly",
        "timestamp": "2025-06-24",
        "endpoints": [
            "/",
            "/health", 
            "/api/v1/auth/signup",
            "/api/v1/auth/login",
            "/api/v1/scripts",
            "/api/v1/test"
        ]
    }

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)

