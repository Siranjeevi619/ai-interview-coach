from interview_coach.rag.document_loader import load_pdf, split_documents
from interview_coach.rag.embeddings import create_embedding_model
from interview_coach.rag.retriever import create_vector_store

pdf_path="./resources/attention.pdf"


documents = load_pdf(pdf_path)
chunks = split_documents(documents)

embedding_model = create_embedding_model()

vector_db = create_vector_store(chunks, embedding_model)

