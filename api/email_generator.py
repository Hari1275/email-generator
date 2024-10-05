from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from portfolio_matcher import match_job_to_portfolio
import re

llm = ChatGroq(
    temperature=0.7,
    groq_api_key='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',
    model_name="llama-3.1-70b-versatile"
)

def clean_content(content):
    # Remove the "content=" prefix and strip quotes
    content = re.sub(r'^content="|\n"$', '', content, flags=re.DOTALL)
    
    # Remove any "Subject:" line
    content = re.sub(r'^Subject:.*\n', '', content)
    
    # Remove any remaining quotes at the beginning or end
    content = content.strip('"')
    
    # Replace escaped newlines with actual newlines
    content = content.replace('\\n', '\n')
    
    # Remove any greeting line starting with "Dear"
    content = re.sub(r'^Dear.*\n', '', content)
    
    # Remove metadata at the end
    content = re.sub(r'\s*additional_kwargs=.*$', '', content, flags=re.DOTALL)
    
    # Remove any remaining metadata
    content = re.sub(r'\s*response_metadata=.*$', '', content, flags=re.DOTALL)
    content = re.sub(r'\s*id=.*$', '', content, flags=re.DOTALL)
    content = re.sub(r'\s*usage_metadata=.*$', '', content, flags=re.DOTALL)
    
    return content.strip()

def generate_email(job_description, template_name="job_application", **kwargs):
    job_data = eval(job_description)
    company_name = job_data.get('Company', 'the company')
    matched_projects = match_job_to_portfolio(job_data['Description'])
    portfolio_links = "\n".join([f"- {url}" for url in matched_projects[:3]])

    if template_name == "job_application":
        prompt = PromptTemplate.from_template(
            """
            Write a concise and attractive cold job application email for the {role} position at {company}. 
            The email should:
            1. Show enthusiasm for the role and company
            2. Highlight 2-3 key skills or experiences relevant to the job
            3. Express interest in an interview
            4. Mention your willingness to provide additional information or references if needed
            Keep the email under 200 words and make it engaging.
            ### EMAIL (NO GREETING OR SIGNATURE):
            """
        )
    elif template_name == "business_outreach":
        prompt = PromptTemplate.from_template(
            """
            Write a concise and attractive business outreach email to {company} regarding their {role} position. 
            The email should:
            1. Introduce TalentSync, an AI-powered recruitment platform
            2. Highlight 2-3 key benefits of using TalentSync for hiring
            3. Suggest a brief call to discuss how TalentSync can help with their hiring needs
            4. Include the following portfolio links of successful placements: {portfolio_links}
            Keep the email under 200 words and make it engaging.
            ### EMAIL (NO GREETING OR SIGNATURE):
            """
        )
    else:
        raise ValueError(f"Unknown template name: {template_name}")

    chain = prompt | llm
    email_content = chain.invoke({
        "role": job_data['Title'],
        "company": company_name,
        "portfolio_links": portfolio_links
    })

    cleaned_content = clean_content(str(email_content))

    email_template = f"""
Dear Hiring Manager,

{cleaned_content}

Best regards,
[Your Name]
    """

    return email_template.strip()
