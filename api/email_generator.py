from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from portfolio_matcher import match_job_to_portfolio
import re
import requests
from bs4 import BeautifulSoup
import logging
import random

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

def clean_company_name(company_name):
    # Remove common suffixes like "Inc", "LLC", etc.
    cleaned = re.sub(r'\b(Inc|LLC|Ltd|Limited|Corp|Corporation)\.?\b', '', company_name, flags=re.IGNORECASE)
    # Replace underscores and hyphens with spaces
    cleaned = re.sub(r'[_-]', ' ', cleaned)
    # Remove extra whitespace
    cleaned = ' '.join(cleaned.split())
    # Handle specific cases like "Thewebpeople In"
    cleaned = re.sub(r'\bIn\b', '', cleaned, flags=re.IGNORECASE).strip()
    # Capitalize words
    cleaned = ' '.join(word.capitalize() for word in cleaned.split())
    return cleaned

def get_company_info(company_name):
    logger.info(f"Attempting to get info for company: {company_name}")
    
    original_name = company_name
    company_name = clean_company_name(company_name)
    logger.info(f"Cleaned company name: {company_name}")
    
    search_engines = [
        (f"https://www.google.com/search?q={company_name}+company", "google"),
        (f"https://www.bing.com/search?q={company_name}+company", "bing"),
        (f"https://duckduckgo.com/html/?q={company_name}+company", "duckduckgo")
    ]
    
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Safari/605.1.15',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    ]

    for search_url, engine in search_engines:
        try:
            logger.info(f"Attempting to get info from {engine} search results for: {company_name}")
            headers = {'User-Agent': random.choice(user_agents)}
            response = requests.get(search_url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            if engine == "google":
                snippets = soup.find_all(['div', 'span', 'p'], class_=['VwiC3b', 'yXK7lf', 'MUxGbd', 'yDYNvb', 'lyLwlc', 'kno-rdesc'])
            elif engine == "bing":
                snippets = soup.find_all(['div', 'p'], class_=['b_snippet', 'b_algoSlug'])
            else:  # duckduckgo
                snippets = soup.find_all(['div', 'a'], class_=['result__snippet', 'result__url'])
            
            for snippet in snippets:
                text = snippet.get_text(strip=True)
                if company_name.lower() in text.lower() and len(text) > 50:
                    logger.info(f"Found company info from {engine}: {text[:100]}...")
                    return text[:200]  # Return first 200 characters
            
            logger.warning(f"No suitable company information found in {engine} search results")
        except Exception as e:
            logger.error(f"Error getting info from {engine} search results: {e}")

    # If all searches fail, generate a generic description
    logger.warning(f"Falling back to generic description for {original_name}")
    return f"{original_name} is a company operating in its industry. " \
           f"They are known for their products or services and are committed to delivering value to their customers."

def generate_email(job_description, template_name="job_application", **kwargs):
    job_data = eval(job_description)
    company_name = job_data.get('Company', 'the company')
    matched_projects = match_job_to_portfolio(job_data['Description'])
    portfolio_links = "\n".join([f"- {url}" for url in matched_projects[:3]])
    
    # Get additional company info
    company_info = get_company_info(company_name)
    print('Company Info:', company_info[:200])

    # Extract customization options
    email_tone = kwargs.get('email_tone', 'professional')
    email_length = kwargs.get('email_length', 'medium')
    include_portfolio = kwargs.get('include_portfolio', True)
    include_experiences = kwargs.get('include_experiences', True)
    emphasis_points = kwargs.get('emphasis_points', [])

    if template_name == "job_application":
        prompt = PromptTemplate.from_template(
            """
            Write a {tone} and {length} cold job application email for the {role} position at {company}. 
            Use this additional information about the company to personalize the email: {company_info}
            The email should:
            1. Start with an attention-grabbing opening related to the company or industry, using the provided company info
            2. Show enthusiasm for the role and company, mentioning a recent company achievement if possible
            3. Highlight 2-3 key skills or experiences relevant to the job, with brief examples
            4. Express interest in an interview, suggesting a specific time (e.g., "next Tuesday at 2 PM")
            5. Close with a clear call-to-action
            
            {portfolio_instruction}
            {experiences_instruction}
            {emphasis_instruction}
            
            Keep the email under 200 words, use short paragraphs, and make it engaging and conversational.
            ### EMAIL (NO GREETING OR SIGNATURE):
            """
        )
    elif template_name == "business_outreach":
        prompt = PromptTemplate.from_template(
            """
            Write a {tone} and {length} business outreach email to {company} regarding their {role} position. 
            Use this additional information about the company to personalize the email: {company_info}
            The email should:
            1. Start with an attention-grabbing opening related to the company's hiring needs or industry challenges, using the provided company info
            2. Introduce TalentSync as an AI-powered recruitment platform that solves specific hiring problems
            3. Highlight 2-3 key benefits of using TalentSync for hiring, with brief success stories or statistics
            4. Suggest a specific time for a brief call (e.g., "this Thursday at 11 AM") to discuss how TalentSync can help with their hiring needs
            5. Include the following portfolio links of successful placements: {portfolio_links}
            6. Close with a clear call-to-action
            
            {portfolio_instruction}
            {experiences_instruction}
            {emphasis_instruction}
            
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
        "portfolio_links": portfolio_links if include_portfolio else "",
        "company_info": company_info,
        "tone": email_tone,
        "length": email_length,
        "portfolio_instruction": "Include portfolio links." if include_portfolio else "Do not include portfolio links.",
        "experiences_instruction": "Include specific experiences." if include_experiences else "Do not include specific experiences.",
        "emphasis_instruction": f"Emphasize the following points: {', '.join(emphasis_points)}" if emphasis_points else ""
    })

    cleaned_content = clean_content(str(email_content))

    email_template = f"""
Dear Hiring Manager,

{cleaned_content}

Best regards,
[Your Name]
    """

    return email_template.strip()