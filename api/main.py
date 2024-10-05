import streamlit as st
from scraper import scrape_job_listings
from api.email_generator import generate_email

def api():
    st.set_page_config(page_title="Cold Email Generator API")

    st.title("Cold Email Generator API")

    endpoint = st.sidebar.selectbox("Select Endpoint", ["Scrape Job", "Generate Email"])

    if endpoint == "Scrape Job":
        scrape_job_api()
    elif endpoint == "Generate Email":
        generate_email_api()

def scrape_job_api():
    st.header("Scrape Job API")
    url = st.text_input("Enter job listing URL")
    if st.button("Scrape"):
        if url:
            with st.spinner("Scraping job listing..."):
                job_listings = scrape_job_listings(url)
            st.json(job_listings)
        else:
            st.error("Please enter a URL")

def generate_email_api():
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
    api()