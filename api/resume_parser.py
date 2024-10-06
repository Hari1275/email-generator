import re
from pdfminer.high_level import extract_text
import io

def parse_resume(file_content, filename):
    if isinstance(file_content, str):
        # If file_content is a string, it's already text content
        text = file_content
    elif filename.lower().endswith('.pdf'):
        text = extract_text(io.BytesIO(file_content))
    else:
        text = file_content.decode('utf-8')

    # Basic parsing logic (you can expand this based on your needs)
    parsed_data = {
        'name': extract_name(text),
        'email': extract_email(text),
        'phone': extract_phone(text),
        'skills': extract_skills(text),
        'experience': extract_experience(text),
    }

    return parsed_data

def extract_name(text):
    # Simple name extraction (first two words)
    words = text.split()
    return ' '.join(words[:2])

def extract_email(text):
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    match = re.search(email_pattern, text)
    return match.group(0) if match else ''

def extract_phone(text):
    phone_pattern = r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'
    match = re.search(phone_pattern, text)
    return match.group(0) if match else ''

def extract_skills(text):
    # This is a simple example. You might want to use a predefined list of skills or NLP techniques for better extraction.
    skills_section = re.search(r'Skills:(.*?)(\n\n|\Z)', text, re.DOTALL | re.IGNORECASE)
    if skills_section:
        skills = skills_section.group(1).strip().split(',')
        return [skill.strip() for skill in skills]
    return []

def extract_experience(text):
    # This is a basic example. You might want to use more sophisticated techniques for better extraction.
    experience_section = re.search(r'Experience:(.*?)(\n\n|\Z)', text, re.DOTALL | re.IGNORECASE)
    if experience_section:
        return experience_section.group(1).strip()
    return ''