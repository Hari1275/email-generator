from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from portfolio_matcher import match_job_to_portfolio
import re
import requests
from bs4 import BeautifulSoup
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

llm = ChatGroq(
    temperature=0.7,
    groq_api_key='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',
    model_name="llama-3.1-70b-versatile"
)

def clean_content(content):
    # Remove the "content=" prefix and strip quotes
    content = re.sub(r'^content=[\'"]|[\'"]$', '', content, flags=re.DOTALL)
    
    # Replace escaped single quotes with regular single quotes
    content = content.replace("\\'", "'")
    
    # Replace escaped newlines with actual newlines
    content = content.replace('\\n', '\n')
    
    # Remove any "Subject:" line
    content = re.sub(r'^Subject:.*\n', '', content)
    
    # Remove any greeting line starting with "Dear"
    content = re.sub(r'^Dear.*\n', '', content)
    
    # Remove metadata at the end
    content = re.sub(r'\s*additional_kwargs=.*$', '', content, flags=re.DOTALL)
    content = re.sub(r'\s*response_metadata=.*$', '', content, flags=re.DOTALL)
    content = re.sub(r'\s*id=.*$', '', content, flags=re.DOTALL)
    content = re.sub(r'\s*usage_metadata=.*$', '', content, flags=re.DOTALL)
    
    return content.strip()

def get_company_info(company_name):
    logger.info(f"Attempting to get info for company: {company_name}")
    
    # Step 1: Try to get info from Wikipedia
    try:
        search_url = f"https://en.wikipedia.org/wiki/{company_name.replace(' ', '_')}"
        logger.info(f"Searching Wikipedia URL: {search_url}")
        response = requests.get(search_url, headers={'User-Agent': 'Mozilla/5.0'})
        
        if response.status_code != 200:
            logger.warning(f"Wikipedia returned status code {response.status_code}")
            raise Exception(f"Wikipedia request failed with status code {response.status_code}")
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Check if we're on a disambiguation page
        if soup.find('table', id='disambigbox'):
            logger.info("Found disambiguation page, searching for most relevant link")
            relevant_link = soup.find('ul', class_='mw-disambig').find('a')
            if relevant_link:
                search_url = f"https://en.wikipedia.org{relevant_link['href']}"
                logger.info(f"Following link to: {search_url}")
                response = requests.get(search_url, headers={'User-Agent': 'Mozilla/5.0'})
                soup = BeautifulSoup(response.content, 'html.parser')
        
        # Try to find the first paragraph of the Wikipedia article
        first_paragraph = soup.find('div', class_='mw-parser-output').find('p', class_=lambda x: x != 'mw-empty-elt')
        
        if first_paragraph:
            # Remove citations and other brackets
            text = re.sub(r'\[.*?\]', '', first_paragraph.text)
            logger.info(f"Successfully extracted Wikipedia info: {text[:100]}...")
            return text[:200]  # Return first 200 characters
        else:
            logger.warning("No suitable paragraph found on Wikipedia page")
            raise Exception("No suitable paragraph found on Wikipedia page")
    except Exception as e:
        logger.error(f"Error fetching from Wikipedia: {e}")

    # Step 2: If Wikipedia fails, try to scrape the company's website
    try:
        logger.info(f"Attempting to scrape company website for: {company_name}")
        search_url = f"https://www.google.com/search?q={company_name}+official+website"
        response = requests.get(search_url, headers={'User-Agent': 'Mozilla/5.0'})
        soup = BeautifulSoup(response.content, 'html.parser')
        company_url = soup.find('div', class_='yuRUbf').find('a')['href']
        
        logger.info(f"Found company URL: {company_url}")
        company_response = requests.get(company_url, headers={'User-Agent': 'Mozilla/5.0'})
        company_soup = BeautifulSoup(company_response.content, 'html.parser')
        
        # Try to find an 'About' section or similar
        about_section = company_soup.find('div', string=re.compile('about', re.IGNORECASE))
        if about_section:
            info = about_section.find_next('p').text[:200]
            logger.info(f"Found 'About' section: {info[:100]}...")
            return info
        else:
            # If no 'About' section, just get the first paragraph
            info = company_soup.find('p').text[:200]
            logger.info(f"No 'About' section found, using first paragraph: {info[:100]}...")
            return info
    except Exception as e:
        logger.error(f"Error scraping company website: {e}")

    # Step 3: If all else fails, generate a generic description
    logger.warning(f"Falling back to generic description for {company_name}")
    return f"{company_name} is a company operating in its industry. " \
           f"They are known for their products or services and are committed to delivering value to their customers."

def generate_email(job_description, template_name="job_application"):
    job_data = eval(job_description)
    company_name = job_data.get('Company', 'the company')
    matched_projects = match_job_to_portfolio(job_data['Description'])
    portfolio_links = "\n".join([f"- {url}" for url in matched_projects[:3]])
    print(company_name)
    # Get additional company info
    company_info = get_company_info(company_name)
    print(company_info)

    if template_name == "job_application":
        prompt = PromptTemplate.from_template(
            """
            Write a concise and attractive cold job application email for the {role} position at {company}. 
            Use this additional information about the company to personalize the email: {company_info}
            The email should:
            1. Start with an attention-grabbing opening related to the company or industry, using the provided company info
            2. Show enthusiasm for the role and company, mentioning a recent company achievement if possible
            3. Highlight 2-3 key skills or experiences relevant to the job, with brief examples
            4. Express interest in an interview, suggesting a specific time (e.g., "next Tuesday at 2 PM")
            5. Close with a clear call-to-action
            Keep the email under 200 words, use short paragraphs, and make it engaging and conversational.
            ### EMAIL (NO GREETING OR SIGNATURE):
            """
        )
    elif template_name == "business_outreach":
        prompt = PromptTemplate.from_template(
            """
            Write a concise and attractive business outreach email to {company} regarding their {role} position. 
            Use this additional information about the company to personalize the email: {company_info}
            The email should:
            1. Start with an attention-grabbing opening related to the company's hiring needs or industry challenges, using the provided company info
            2. Introduce TalentSync as an AI-powered recruitment platform that solves specific hiring problems
            3. Highlight 2-3 key benefits of using TalentSync for hiring, with brief success stories or statistics
            4. Suggest a specific time for a brief call (e.g., "this Thursday at 11 AM") to discuss how TalentSync can help with their hiring needs
            5. Include the following portfolio links of successful placements: {portfolio_links}
            6. Close with a clear call-to-action
            Keep the email under 200 words, use short paragraphs, and make it engaging and conversational.
            ### EMAIL (NO GREETING OR SIGNATURE):
            """
        )
    else:
        raise ValueError(f"Unknown template name: {template_name}")

    chain = prompt | llm
    email_content = chain.invoke({
        "role": job_data['Title'],
        "company": company_name,
        "portfolio_links": portfolio_links,
        "company_info": company_info
    })

    cleaned_content = clean_content(str(email_content))

    email_template = f"""
Dear Hiring Manager,

{cleaned_content}

Best regards,
[Your Name]
    """

    return email_template.strip()
