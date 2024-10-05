import streamlit as st
import requests

st.title("Cold Email Generator SaaS")

url = st.text_input("Enter the company's career page URL:")

if url:
    try:
        with st.spinner("Scraping job listings..."):
            response = requests.post("http://localhost:8501/scrape_job", json={"url": url})
            job_listings = response.json()
        
        if job_listings:
            st.success(f"Found {len(job_listings)} job listings!")
            st.write("Job Listings:")
            for job in job_listings:
                st.write("---")
                for key, value in job.items():
                    if key == "Responsibilities" and isinstance(value, list):
                        st.write(f"**{key}:**")
                        for resp in value:
                            st.write(f"- {resp}")
                    else:
                        st.write(f"**{key}:** {value}")
            
            selected_job = st.selectbox("Select a job to generate an email for:", [job['Title'] for job in job_listings])
            if st.button("Generate Email"):
                with st.spinner("Generating email..."):
                    selected_job_data = next(job for job in job_listings if job['Title'] == selected_job)
                    response = requests.post("http://localhost:8501/generate_email", json={"job_description": str(selected_job_data)})
                    email = response.json()["email"]
                st.write("Generated Email:", email)
        else:
            st.warning("No job listings found on this page. The page structure might be different from what we expected. Please try a different URL or contact support for assistance.")
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        st.error("Please try again or contact support if the issue persists.")