BUSINESS_OUTREACH_TEMPLATE = """
Dear {recipient_name},

{custom_intro}

{email_signoff}
{user_name}
{user_position}
{user_company}
{contact_info}
"""

def generate_business_outreach_email(**kwargs):
    defaults = {
        'recipient_name': 'Hiring Manager',
        'custom_intro': '',
        'email_signoff': 'Best regards,',
        'user_name': '[Your Name]',
        'user_position': '[Your Position]',
        'user_company': '[Your Company]',
        'contact_info': '[Your Contact Info]'
    }
    
    for key, value in defaults.items():
        if key not in kwargs or not kwargs[key]:
            kwargs[key] = value
    
    return BUSINESS_OUTREACH_TEMPLATE.format(**kwargs)