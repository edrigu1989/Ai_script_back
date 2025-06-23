from fastapi import FastAPI, Depends, HTTPException, Header, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv

load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Starting up AI Script Strategist API...")
    yield
    # Shutdown
    print("Shutting down...")

app = FastAPI(
    title="AI Script Strategist API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration - Allow all origins for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "AI Script Strategist API", "version": "1.0.0", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "AI Script Strategist API"}

# Basic auth endpoint for testing
@app.post("/api/v1/auth/test")
async def test_auth():
    return {"message": "Auth endpoint working", "status": "success"}

# Basic scripts endpoint for testing
@app.get("/api/v1/scripts")
async def get_scripts():
    return {"scripts": [], "message": "Scripts endpoint working"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)

