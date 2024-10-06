import os

# Set environment variables
os.environ['PINECONE_API_KEY'] = 'e5886319-f1b9-449e-918e-39e09e5a3314'
os.environ['PINECONE_ENVIRONMENT'] = 'us-east-1'
os.environ['USER_AGENT'] = 'Cold Email Generator SaaS (https://github.com/yourusername/your-repo)'

from api.main import app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9000)