from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

llm = ChatGroq(
    temperature=0,
    groq_api_key='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',
    model_name="llama-3.1-70b-versatile"
)

def generate_email(job_description):
    prompt = PromptTemplate(
        input_variables=["job_description"],
        template="Generate a personalized cold email for the following job description:\n{job_description}\n\nEmail:"
    )
    chain = LLMChain(llm=llm, prompt=prompt)
    email = chain.run(job_description=job_description)
    return email