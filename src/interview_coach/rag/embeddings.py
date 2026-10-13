import os

from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings

load_dotenv()


def create_embedding_model() -> HuggingFaceEmbeddings:
    model_name = os.getenv("EMBEDDING_MODEL_NAME")
    if not model_name:
        raise ValueError("EMBEDDING_MODEL_NAME not set")
    return HuggingFaceEmbeddings(
        model_name=model_name
    )