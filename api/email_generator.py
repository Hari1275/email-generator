from langchain_groq import ChatGroq
from email_templates import generate_custom_email
from langchain.schema import HumanMessage

llm = ChatGroq(
    temperature=0,
    groq_api_key='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',
    model_name="llama-3.1-70b-versatile"
)

def generate_email(job_description, template_name="job_application", **kwargs):
    custom_intro = llm.invoke([HumanMessage(content=f"Generate a custom introduction for this job: {job_description}")]).content
    job_specific_skills = llm.invoke([HumanMessage(content=f"List relevant skills for this job: {job_description}")]).content
    
    email = generate_custom_email(
        template_name,
        role=kwargs.get('role', 'the position'),
        company=kwargs.get('company', 'your company'),
        custom_intro=custom_intro,
        job_specific_skills=job_specific_skills,
        portfolio_links=kwargs.get('portfolio_links', '')
    )
    
    return email