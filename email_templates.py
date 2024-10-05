templates = {
    "job_application": """
    Dear Hiring Manager,

    {custom_intro}

    {job_specific_skills}

    Here are some relevant projects from my portfolio:
    {portfolio_links}

    Thank you for considering my application. I look forward to the opportunity to discuss how I can contribute to your team.

    Best regards,
    [Your Name]
    """,
    "business_outreach": """
    Dear {recipient_name},

    I hope this email finds you well. I recently came across {company} and was impressed by your work in {industry}. {custom_intro}

    {service_offering}

    Here are some relevant projects from my portfolio that demonstrate our expertise:
    {portfolio_links}

    I would love the opportunity to discuss how we can collaborate. Would you be available for a brief call next week?

    Best regards,
    [Your Name]
    """
}

def generate_custom_email(template_name, **kwargs):
    template = templates.get(template_name)
    if not template:
        raise ValueError("Template not found")
    return template.format(**kwargs)