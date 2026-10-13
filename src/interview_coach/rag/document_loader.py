from os import path

from langchain_community.document_loaders import PyPDFLoader
from pathlib import Path

from langchain_text_splitters import RecursiveCharacterTextSplitter


def load_pdf(file_path : str):
    if not path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    loader = PyPDFLoader(str(Path(file_path)))

    document = loader.load()

    return document


def split_documents(documents : list) -> list:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=100,

    )

    chunks = splitter.split_documents(documents)

    if not chunks:
        raise Exception("No chunks were created from documents")

    return chunks


