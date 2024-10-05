templates = {
    "job_application": """
Dear {recipient_name},

{custom_intro}

I am excited to apply for the {role} position at {company}. {relevant_experience}

Key skills relevant to this position:
{job_specific_skills}

{company_specific_interest}

Thank you for considering my application. I look forward to the opportunity to discuss how I can contribute to {company}'s success.

{email_signoff}
{contact_info}
    """,
    "business_outreach": """
Dear {recipient_name},

{custom_intro}

At {user_company}, we specialize in {your_services}. Our approach has consistently delivered:
{value_proposition}

{case_study}

I believe {company} could benefit from our services in the following way:
{potential_benefit}

{portfolio_section}

Would you be available for a brief 15-minute call next week to discuss how we can tailor our solutions to your specific needs?

Thank you for your time. I look forward to the possibility of collaborating with {company}.

{email_signoff}
{contact_info}
    """
}

def generate_custom_email(template_name, **kwargs):
    template = templates.get(template_name)
    if not template:
        raise ValueError("Template not found")
    
    # Remove empty values
    kwargs = {k: v for k, v in kwargs.items() if v}
    
    # Set default values only if they're not provided
    defaults = {
        'user_name': 'Applicant',
        'user_position': 'Job Seeker',
        'user_company': 'Current Company',
        'recipient_name': 'Hiring Manager',
        'portfolio_section': '',
        'email_signoff': 'Best regards,',
        'contact_info': ''
    }
    
    # Update kwargs with defaults for missing values
    for key, value in defaults.items():
        if key not in kwargs:
            kwargs[key] = value
    
    return template.format(**kwargs)