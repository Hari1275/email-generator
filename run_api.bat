@echo off
cd /d %~dp0
set PYTHONPATH=%PYTHONPATH%;%CD%
set USER_AGENT=Cold Email Generator SaaS (https://github.com/yourusername/your-repo)
set PINECONE_API_KEY=e5886319-f1b9-449e-918e-39e09e5a3314
set PINECONE_ENVIRONMENT=us-east-1
python api\main.py