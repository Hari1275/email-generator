from langchain_community.document_loaders import WebBaseLoader
from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq
import json
import logging
import os
import re
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set a default User-Agent
os.environ['USER_AGENT'] = 'Cold Email Generator SaaS (https://github.com/yourusername/your-repo)'

# Initialize LLaMA 3.1 model
llm = ChatGroq(
    temperature=0,
    groq_api_key='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',
    model_name="llama-3.1-70b-versatile"
)

def clean_json_string(json_string):
    json_string = json_string.strip()
    json_string = re.sub(r'^```json\s*|\s*```$', '', json_string, flags=re.MULTILINE)
    return json_string

def extract_company_name(url):
    parsed_url = urlparse(url)
    domain = parsed_url.netloc
    # Remove common domain extensions and 'www'
    company_name = re.sub(r'(\.com|\.org|\.net|\.io|\.co|\.jobs|www\.)', '', domain)
    # Split by remaining dots or hyphens and capitalize each word
    company_name = ' '.join(word.capitalize() for word in re.split(r'[.-]', company_name))
    return company_name

def scrape_linkedin_job(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract job details
        title = soup.find('h1', class_='top-card-layout__title').text.strip()
        company = soup.find('a', class_='topcard__org-name-link').text.strip()
        location = soup.find('span', class_='topcard__flavor--bullet').text.strip()
        description = soup.find('div', class_='show-more-less-html__markup').text.strip()

        # Extract other details if available
        employment_type = "Not specified"
        experience = "Not specified"
        skills = "Not specified"
        responsibilities = ["Not specified"]

        job_listing = {
            "Title": title,
            "Company": company,
            "Location": location,
            "Employment Type": employment_type,
            "Description": description[:200] + "...",
            "Experience": experience,
            "Skills": skills,
            "Responsibilities": responsibilities
        }

        return [job_listing]
    except Exception as e:
        logger.error(f"Error scraping LinkedIn job listing: {str(e)}")
        return []

def scrape_job_listings(url):
    if 'linkedin.com' in url:
        return scrape_linkedin_job(url)

    try:
        loader = WebBaseLoader(url)
        page_data = loader.load()[0].page_content

        company_name = extract_company_name(url)

        prompt_extract = PromptTemplate.from_template(
            """
            ### SCRAPED TEXT FROM WEBSITE:
            {page_data}
            ### INSTRUCTION:
            The scraped text is from the career's page of {company_name}.
            Your job is to extract the job posting and return it in JSON format containing the 
            following keys: `role`, `location`, `employment_type`, `experience`, `skills`, `responsibilities`, and `description`.
            If you can't find information for a specific key, use "Not specified" as the value.
            Only return the valid JSON, nothing else. Do not include any explanations or markdown formatting.
            ### VALID JSON (NO PREAMBLE):    
            """
        )

        chain_extract = prompt_extract | llm 
        res = chain_extract.invoke(input={'page_data': page_data, 'company_name': company_name})

        cleaned_json_string = clean_json_string(res.content)
        logger.info(f"Cleaned JSON string: {cleaned_json_string}")

        try:
            job_data = json.loads(cleaned_json_string)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from LLM response. Error: {str(e)}")
            logger.error(f"Response content: {res.content}")
            job_data = {
                'role': 'Parsing Error',
                'location': 'Not specified',
                'employment_type': 'Not specified',
                'experience': 'Not specified',
                'skills': 'Not specified',
                'responsibilities': ['Not specified'],
                'description': 'Failed to parse job details. Please try again or contact support.'
            }

        job_listing = {
            "Title": job_data.get('role', 'No title found'),
            "Location": job_data.get('location', 'Location not specified'),
            "Employment Type": job_data.get('employment_type', 'Not specified'),
            "Experience": job_data.get('experience', 'Not specified'),
            "Skills": job_data.get('skills', 'Not specified'),
            "Description": job_data.get('description', 'No description found')[:200] + "...",
            "Responsibilities": job_data.get('responsibilities', ['Not specified']),
            "Company": company_name
        }

        logger.info(f"Found job listing for {company_name}: {job_data.get('role', 'No title found')}")
        return [job_listing]  # Return as a list to maintain compatibility with the existing app structure
    except Exception as e:
        logger.error(f"Error scraping job listing: {str(e)}")
        return []