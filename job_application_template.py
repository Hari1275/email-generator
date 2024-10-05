JOB_APPLICATION_TEMPLATE = """
Dear {recipient_name},

{custom_intro}

Thank you for considering my application. I look forward to the opportunity to discuss how I can contribute to {company}'s success.

{email_signoff}
{user_name}
{contact_info}
"""

def generate_job_application_email(**kwargs):
    # Set default values only if they're not provided
    defaults = {
        'recipient_name': 'Hiring Manager',
        'custom_intro': '',
        'company': 'your company',
        'email_signoff': 'Best regards,',
        'user_name': '',
        'contact_info': ''
    }
    
    # Update kwargs with defaults for missing values
    for key, value in defaults.items():
        if key not in kwargs or not kwargs[key]:
            kwargs[key] = value
    
    # Format contact info
    if kwargs['contact_info']:
        kwargs['contact_info'] = f"\n{kwargs['contact_info']}"
    
    return JOB_APPLICATION_TEMPLATE.format(**kwargs)