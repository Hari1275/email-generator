from langchain_community.document_loaders import WebBaseLoader
from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq
import json
import logging
import os
import re

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

def scrape_job_listings(url):
    try:
        loader = WebBaseLoader(url)
        page_data = loader.load()[0].page_content

        prompt_extract = PromptTemplate.from_template(
            """
            ### SCRAPED TEXT FROM WEBSITE:
            {page_data}
            ### INSTRUCTION:
            The scraped text is from the career's page of a website.
            Your job is to extract the job posting and return it in JSON format containing the 
            following keys: `role`, `location`, `employment_type`, `experience`, `skills`, `responsibilities`, and `description`.
            If you can't find information for a specific key, use "Not specified" as the value.
            Only return the valid JSON, nothing else. Do not include any explanations or markdown formatting.
            ### VALID JSON (NO PREAMBLE):    
            """
        )

        chain_extract = prompt_extract | llm 
        res = chain_extract.invoke(input={'page_data': page_data})

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
                'skills': [],
                'responsibilities': [],
                'description': 'Failed to parse job details. Please try again or contact support.'
            }

        job_listing = {
            "Title": job_data.get('role', 'No title found'),
            "Location": job_data.get('location', 'Location not specified'),
            "Employment Type": job_data.get('employment_type', 'Employment type not specified'),
            "Description": job_data.get('description', 'No description found')[:200] + "...",
            "Experience": job_data.get('experience', 'No experience requirements specified'),
            "Skills": job_data.get('skills', 'No skills specified'),
            "Responsibilities": job_data.get('responsibilities', ['No responsibilities specified'])
        }

        logger.info(f"Found job listing: {job_data.get('role', 'No title found')}")
        return [job_listing]  # Return as a list to maintain compatibility with the existing app structure
    except Exception as e:
        logger.error(f"Error scraping job listing: {str(e)}")
        return []

# You can add more specific scraping functions for different website structures here