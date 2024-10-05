import streamlit as st
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from scraper import scrape_job_listings
from api.email_generator import generate_email
import uvicorn
from pydantic import BaseModel

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

@app.post("/scrape_job")
async def scrape_job(job_url: JobURL):
    result = scrape_job_listings(job_url.url)
    return result

@app.post("/generate_email")
async def generate_email_api(job_desc: JobDescription):
    email = generate_email(job_desc.job_description)
    return {"email": email}

def run_fastapi():
    uvicorn.run(app, host="0.0.0.0", port=8000)

def streamlit_ui():
    st.title("Cold Email Generator API")
    endpoint = st.sidebar.selectbox("Select Endpoint", ["Scrape Job", "Generate Email"])

    if endpoint == "Scrape Job":
        scrape_job_ui()
    elif endpoint == "Generate Email":
        generate_email_ui()

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
    if st.button("Generate Email"):
        if job_description:
            with st.spinner("Generating email..."):
                email = generate_email(job_description)
            st.text_area("Generated Email", email, height=300)
        else:
            st.error("Please enter a job description")

if __name__ == "__main__":
    import threading
    fastapi_thread = threading.Thread(target=run_fastapi)
    fastapi_thread.start()
    streamlit_ui()