
from langchain_core.prompts import ChatPromptTemplate


rag_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are a technical interview assistant.

            Answer the user's question using the supplied context.
            
            Rules:
            - Base factual claims about the paper on the supplied context.
            - If the context does not contain enough information, say so.
            - Do not invent information or claim that the paper states
              something that is not supported by the context.
            - Explain technical concepts clearly.
            """
                    ),
                    (
                        "human",
                        """Context:
            {context}
            
            Question:
            {question}
            
            Provide a clear, technically accurate answer."""
        ),
    ]
)
