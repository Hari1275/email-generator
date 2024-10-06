import streamlit as st
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from api.email_generator import generate_email
from api.scraper import scrape_job_listings
import logging

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
            template_name=request.template_name
        )
        return {"email": email}
    except Exception as e:
        logger.error(f"Error generating email: {str(e)}")
        raise HTTPException(status_code=500, detail="Error generating email")

def run_fastapi():
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
def streamlit_ui():
    st.title("Cold Email Generator API")
    endpoint = st.sidebar.selectbox("Select Endpoint", ["Scrape Job", "Generate Email", "Match Portfolio"])

    if endpoint == "Scrape Job":
        scrape_job_ui()
    elif endpoint == "Generate Email":
        generate_email_ui()
    elif endpoint == "Match Portfolio":
        match_portfolio_ui()

def scrape_job_ui():
    st.header("Scrape Job API")
    url = st.text_input("Enter job listing URL")
    if st.button("Scrape"):
        if url:
            with st.spinner("Scraping job listing..."):
                job_listings = scrape_job_listings(url)
            st.json(job_listings)
        else:
            st.error("Please enter a URL")

def generate_email_ui():
    st.header("Generate Email API")
    job_description = st.text_area("Enter job description")
    template_name = st.selectbox("Select email template", ["job_application", "business_outreach"])
    if st.button("Generate Email"):
        if job_description:
            with st.spinner("Generating email..."):
                email = generate_email(job_description, template_name=template_name)
            st.text_area("Generated Email", email, height=300)
        else:
            st.error("Please enter a job description")

def match_portfolio_ui():
    st.header("Match Portfolio API")
    job_description = st.text_area("Enter job description")
    if st.button("Match Portfolio"):
        if job_description:
            with st.spinner("Matching portfolio..."):
                matched_projects = match_job_to_portfolio(job_description)
            st.json({"matched_projects": matched_projects})
        else:
            st.error("Please enter a job description")

if __name__ == "__main__":
    import threading
    fastapi_thread = threading.Thread(target=run_fastapi)
    fastapi_thread.start()
    streamlit_ui()
