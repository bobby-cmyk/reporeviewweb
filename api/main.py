from fastapi import FastAPI, Form, HTTPException
from pydantic import BaseModel
import requests
import time
from mangum import Mangum  # Add this import
import logging
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


app = FastAPI()

# Serve static files from the "static" directory
app.mount("/static", StaticFiles(directory="static"), name="static")

# Pydantic model for the response structure
class RepoAnalysisResponse(BaseModel):
    model: str
    duration: float
    feedback: str
    error: str = None

@app.get("/")
def read_root():
    return RedirectResponse(url='/static/index.html')

# Change the route to '/'
@app.post("/api/analyze")
async def analyze_repo(github_url: str = Form(...)) -> RepoAnalysisResponse:
    logger.info(f"Received request with github_url: {github_url}")
    start_time = time.time()
    
    try:
        response = requests.get(github_url)
        if response.status_code != 200:
            raise HTTPException(status_code=404, detail="GitHub repository not found.")
        
        # Dummy logic for feedback, replace this with actual analysis
        feedback = f"Repository at {github_url} has been analyzed."
    
    except Exception as e:
        return RepoAnalysisResponse(
            model="None",
            duration=time.time() - start_time,
            feedback="",
            error=str(e)
        )
    
    return RepoAnalysisResponse(
        model="RepoAnalyzerModel",
        duration=time.time() - start_time,
        feedback=feedback,
        error=None
    )

# Add the Mangum handler
handler = Mangum(app)
