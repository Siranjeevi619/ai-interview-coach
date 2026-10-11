import os

from langchain_groq import ChatGroq

model = os.getenv("GROQ_MODEL")
api_key = os.getenv("GROQ_API_KEY")
if not api_key or not model:
    raise ValueError("API key not set")


llm = ChatGroq(model=model, api_key=api_key, temperature=0.5)

