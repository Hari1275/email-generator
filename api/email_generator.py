from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from portfolio_matcher import match_job_to_portfolio
import re
import requests
from bs4 import BeautifulSoup

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
    # This is a placeholder function. In a real implementation, you'd use a more robust method to fetch company info.
    url = f"https://en.wikipedia.org/wiki/{company_name.replace(' ', '_')}"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    summary = soup.find('p').text if soup.find('p') else ""
    return summary[:200]  # Return first 200 characters as a brief summary

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
