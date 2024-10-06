import streamlit as st
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import logging
from typing import List

# Use relative imports
from .email_generator import generate_email
from .scraper import scrape_job_listings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class JobURL(BaseModel):
    url: str

class EmailRequest(BaseModel):
    job_description: str
    template_name: str = "job_application"
    email_tone: str = "professional"
    email_length: str = "medium"
    include_portfolio: bool = True
    include_experiences: bool = True
    emphasis_points: List[str] = []

@app.post("/scrape_job")
async def scrape_job(job_url: JobURL):
    try:
        jobs = scrape_job_listings(job_url.url)
        return jobs
    except Exception as e:
        logger.error(f"Error scraping jobs: {str(e)}")
        raise HTTPException(status_code=500, detail="Error scraping jobs")

@app.post("/generate_email")
async def generate_email_api(request: EmailRequest):
    try:
        email = generate_email(
            job_description=request.job_description,
            template_name=request.template_name,
            email_tone=request.email_tone,
            email_length=request.email_length,
            include_portfolio=request.include_portfolio,
            include_experiences=request.include_experiences,
            emphasis_points=request.emphasis_points
        )
        return {"email": email}
    except Exception as e:
        logger.error(f"Error generating email: {str(e)}")
        raise HTTPException(status_code=500, detail="Error generating email")

# Remove the streamlit_ui function and related functions if you're not using Streamlit with FastAPI

# Keep this line at the end
app = app
