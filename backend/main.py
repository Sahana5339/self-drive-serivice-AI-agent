import os
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from services.service import Service
from routers import cars
from routers import chat_gemini as chat
from repos.repo import Repo
from constants import DB_NAME

repo = Repo(DB_NAME)
service = Service(repo)

# Configure allowed origins for CORS
ALLOWED_ORIGINS = [
    "*"  # Only use this for development - remove for production
]

# Create FastAPI app
app = FastAPI(title="Car Management API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes first
app.include_router(cars.router, prefix="/cars", tags=["Cars"])
app.include_router(chat.router, tags=["Chat"])

# Mount static files (frontend) - this should be last
app.mount("/", StaticFiles(directory="../frontend", html=True), name="static")

if __name__ == "__main__":
    # Use the PORT environment variable provided by Cloud Run, defaulting to 8080
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
 