from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings


COLLECTION_NAME = "attention_is_all_you_need"
PERSIST_DIRECTORY = "./chroma_db"


def create_vector_store(chunks , embedding_model):

    vector_store = Chroma.from_documents(
        embedding=embedding_model,
        documents=chunks,
        collection_name="attention_is_all_you_need",
        persist_directory="./chroma_db",
    )
    return vector_store


def load_vector_store(
    embedding_model: HuggingFaceEmbeddings,
) -> Chroma:
    return Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embedding_model,
        persist_directory=PERSIST_DIRECTORY,
    )



def retrieve_documents(query: str,vector_store: Chroma,k: int = 3,) -> list:
    if not query.strip():
        raise ValueError("Search query cannot be empty.")

    if k < 1:
        raise ValueError("k must be at least 1.")

    retriever = vector_store.as_retriever(
        search_kwargs={"k": k}
    )

    return retriever.invoke(query)
