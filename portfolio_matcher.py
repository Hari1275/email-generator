import os
from sentence_transformers import SentenceTransformer
from pinecone import Pinecone, ServerlessSpec
import numpy as np

# Use os.environ instead of os.getenv
pc = Pinecone(api_key=os.environ['PINECONE_API_KEY'])
index_name = "portfolio-projects"

# Load pre-trained model
model = SentenceTransformer('all-MiniLM-L6-v2')

def create_index_if_not_exists():
    if index_name not in pc.list_indexes().names():
        pc.create_index(
            name=index_name,
            dimension=384,  # Dimension for 'all-MiniLM-L6-v2' model
            metric="cosine",
            spec=ServerlessSpec(
                cloud="aws",
                region="us-east-1"  # Replace with your preferred region
            )
        )

def index_portfolio_projects(projects):
    create_index_if_not_exists()
    index = pc.Index(index_name)
    vectors = []
    for i, project in enumerate(projects):
        vector = model.encode(project['description']).tolist()
        vectors.append((str(i), vector, {"url": project['url']}))
    index.upsert(vectors=vectors)
    print(f"Indexed {len(projects)} portfolio projects")

def match_job_to_portfolio(job_description):
    index = pc.Index(index_name)
    job_vector = model.encode(job_description).tolist()
    results = index.query(vector=job_vector, top_k=3, include_metadata=True)
    matched_projects = [match.metadata['url'] for match in results.matches]
    print(f"Matched projects: {matched_projects}")
    return matched_projects

# Sample portfolio projects for testing
sample_projects = [
    {"description": "Web development project using React and Node.js", "url": "https://example.com/project1"},
    {"description": "Machine learning model for image classification", "url": "https://example.com/project2"},
    {"description": "Mobile app development using Flutter", "url": "https://example.com/project3"},
]

# Initialize the index and add sample projects
create_index_if_not_exists()
index_portfolio_projects(sample_projects)