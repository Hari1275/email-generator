import streamlit as st
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from scraper import scrape_job_listings
from api.email_generator import generate_email
from portfolio_matcher import match_job_to_portfolio
import uvicorn
from pydantic import BaseModel
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

class JobDescription(BaseModel):
    job_description: str

class EmailRequest(BaseModel):
    job_description: str
    template_name: str = "job_application"
    user_company: str = ""
    recipient_name: str = ""
    user_name: str = ""
    user_position: str = ""
    education_level: str = ""
    university: str = ""
    field_of_study: str = ""

@app.post("/scrape_job")
async def scrape_job(job_url: JobURL):
    result = scrape_job_listings(job_url.url)
    return result

@app.post("/generate_email")
async def generate_email_api(request: EmailRequest):
    matched_projects = match_job_to_portfolio(request.job_description)
    portfolio_links = "\n".join([f"- {url}" for url in matched_projects])
    email = generate_email(
        request.job_description,
        template_name=request.template_name,
        portfolio_links=portfolio_links if request.template_name == "business_outreach" else "",
        company=request.user_company,
        recipient_name=request.recipient_name,
        user_name=request.user_name,
        user_position=request.user_position,
        user_company=request.user_company,
        education_level=request.education_level,
        university=request.university,
        field_of_study=request.field_of_study
    )
    return {"email": email}

@app.post("/match_portfolio")
async def match_portfolio(job_desc: JobDescription):
    try:
        matched_projects = match_job_to_portfolio(job_desc.job_description)
        return {"matched_projects": matched_projects}
    except Exception as e:
        logger.error(f"Error matching portfolio: {str(e)}")
        return {"error": "Unable to match portfolio at this time. Please try again later."}

def run_fastapi():
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