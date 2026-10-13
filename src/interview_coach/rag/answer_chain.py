from index_pdf import embedding_model
from interview_coach.ai.model import llm
from interview_coach.ai.prompts.rag import rag_prompt
from interview_coach.rag.embeddings import create_embedding_model
from interview_coach.rag.retriever import load_vector_store, retrieve_documents


def rag_chain():
    embedding_model = create_embedding_model()
    vector_store = load_vector_store(embedding_model=embedding_model)

    return vector_store


def answer(question):

    vector_store = rag_chain()
    document = retrieve_documents(query=question,
                                  vector_store=vector_store,
                                  k=3)

    context = "\n\n".join(doc.page_content for doc in document )

    chain  = rag_prompt | llm

    response = chain.invoke({
        "context": context,
        "question": question,
    })

    return {
        "answer": response.content,
        "source":[
            {
                "page":doc.metadata.get("page"),
                "source":doc.metadata.get("source"),
                "text":doc.page_content
            }

            for doc in document
        ]
    }

