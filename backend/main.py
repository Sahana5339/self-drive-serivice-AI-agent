import os
import uvicorn
from google.adk.cli.fast_api import get_fast_api_app
from services.service import Service
from routers import cars
from repos.repo import Repo
from constants import DB_NAME


repo = Repo(DB_NAME)
service = Service(repo)

# Get the directory where main.py is located
AGENT_DIR = os.path.dirname(os.path.abspath(__file__))

# Session service URI (e.g., SQLite)
# SESSION_SERVICE_URI = "sqlite:///./sessions.db"

# Configure allowed origins for CORS - Add your domains here
ALLOWED_ORIGINS = [
    "*"  # Only use this for development - remove for production
]

# Set web=True if you intend to serve a web interface, False otherwise
SERVE_WEB_INTERFACE = True

# Call the function to get the FastAPI app instance
# The agent_dir should point to the directory containing main.py
# ADK will automatically discover the weather_agent folder within it
app = get_fast_api_app(
    agents_dir=AGENT_DIR,  # This points to sample-agent-v2/ directory
    # session_service_uri=SESSION_SERVICE_URI,
    allow_origins=ALLOWED_ORIGINS,  # This is the key CORS configuration
    web=SERVE_WEB_INTERFACE,
)

app.include_router(cars.router, prefix="/cars", tags=["Cars"])

if __name__ == "__main__":
    # Use the PORT environment variable provided by Cloud Run, defaulting to 8080
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
 