from langchain_chroma import Chroma


def create_vector_store(chunks , embedding_model):

    vector_store = Chroma.from_documents(
        embedding=embedding_model,
        documents=chunks,
        collection_name="attention_is_all_you_need",
        persist_directory="./chroma_db",
    )
    return vector_store
