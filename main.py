# app/main.py
import os
import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles # Import StaticFiles
from fastapi.responses import FileResponse  # Import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import logging # Import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Attempt to import the router
try:
    from app.routes import newsletter
    ROUTER_AVAILABLE = True
    logger.info("Newsletter router imported successfully.")
except ImportError as e:
    logger.error(f"Error importing newsletter router: {e}", exc_info=True)
    ROUTER_AVAILABLE = False
except Exception as e:
    logger.error(f"An unexpected error occurred during router import: {e}", exc_info=True)
    ROUTER_AVAILABLE = False

# Load environment variables
load_dotenv()
logger.info(".env file loaded (if exists).")

# Initialize FastAPI app
app = FastAPI(
    title="Newsletter Generator API",
    description="API for generating newsletters using AI and serving the frontend",
    version="1.0.0"
)

# Configure CORS (Allow all for development)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allows all origins
    allow_credentials=True,
    allow_methods=["*"], # Allows all methods
    allow_headers=["*"], # Allows all headers
)
logger.info("CORS middleware configured to allow all origins.")

# Include API router only if it was successfully imported
if ROUTER_AVAILABLE:
    app.include_router(newsletter.router) # This handles /newsletter/* routes
    logger.info("Included newsletter API router.")
else:
    logger.warning("Newsletter API router could not be loaded and was not included.")

# --- Static File Serving ---

# Mount static files (like CSS, JS images if you add them later) from the 'src' directory
# These will be accessible under the path /static
# Example: src/style.css would be available at http://localhost:8000/static/style.css
if os.path.exists("src"):
    app.mount("/static", StaticFiles(directory="src"), name="static")
    logger.info("Mounted static files directory 'src' at /static path.")
else:
    logger.warning("Directory 'src' not found, static files will not be served from /static.")

# Serve the index.html file at the root path
@app.get("/", include_in_schema=False) # exclude from OpenAPI docs
async def serve_index():
    html_file_path = "src/index.html"
    if os.path.exists(html_file_path):
        return FileResponse(html_file_path)
    else:
        # Fallback if index.html doesn't exist
        logger.error("src/index.html not found.")
        return {"message": "Welcome to the API, but index.html is missing.", "router_loaded": ROUTER_AVAILABLE}

# Add a health check or basic API root endpoint if needed
@app.get("/api/status", tags=["API Status"])
async def api_status():
    return {"status": "API is running", "newsletter_router_loaded": ROUTER_AVAILABLE}


# Run the app
if __name__ == "__main__":
    logger.info("Starting Uvicorn server...")
    # Run without reload first to confirm it works
    # To enable reload later: uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
    uvicorn.run(app, host="0.0.0.0", port=8000)
