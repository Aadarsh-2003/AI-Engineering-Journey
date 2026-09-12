import os
import re

from dotenv import load_dotenv

load_dotenv()

import chromadb
from google import genai
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction


# ==================================================
# 1. Source Document
# ==================================================

text = """
FastAPI is a modern Python framework for building APIs.
It supports automatic API documentation.
You can define request and response models using Pydantic.
Authentication can be implemented using OAuth2 and JWT tokens.
FastAPI applications can be deployed using Docker.
PostgreSQL can be used as the application's database.
"""

EVALUATION_QUESTIONS = [
    {
        "question": "How do I implement authentication?",
        "relevant": True
    },
    {
        "question": "How do I deploy FastAPI?",
        "relevant": True
    },
    {
        "question": "What is Pydantic?",
        "relevant": True
    },
    {
        "question": "How do I configure Redis?",
        "relevant": False
    },
    {
        "question": "What is Kubernetes?",
        "relevant": False
    }
]


# ==================================================
# 2. Configuration
# ==================================================

CHUNK_SIZE = 100
TOP_K = 3
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
COLLECTION_NAME = "document_chunks"
RELEVANCE_THRESHOLD = 0.7


# ==================================================
# 3. Initialize Clients
# ==================================================

chroma_client = chromadb.Client()

gen_client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

embedding_function = SentenceTransformerEmbeddingFunction(
    model_name=EMBEDDING_MODEL
)


# ==================================================
# 4. Chunking
# ==================================================

def split_into_chunks(text, chunk_size):
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())

    chunks = []
    current_chunk = []

    for sentence in sentences:

        current_text = " ".join(current_chunk)

        if not current_chunk:
            current_chunk.append(sentence)

        elif len(current_text) + len(sentence) + 1 <= chunk_size:
            current_chunk.append(sentence)

        else:
            chunks.append(" ".join(current_chunk))

            # Keep the last sentence as overlap
            current_chunk = [current_chunk[-1], sentence]

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks


# ==================================================
# 5. Create Chunks
# ==================================================

chunks = split_into_chunks(
    text,
    CHUNK_SIZE
)

print("Created chunks:\n")

for i, chunk in enumerate(chunks):
    print(f"Chunk {i}: {chunk}\n")


# ==================================================
# 6. Create ChromaDB Collection
# ==================================================

collection = chroma_client.create_collection(
    name=COLLECTION_NAME,
    embedding_function=embedding_function
)


# ==================================================
# 7. Store Chunks
# ==================================================

collection.add(
    ids=[str(i) for i in range(len(chunks))],
    documents=chunks,
    metadatas=[
        {
            "source": "fastapi_notes",
            "chunk_number": i,
            "topic": "fastapi"
        }
        for i in range(len(chunks))
    ]
)


# ==================================================
# 8. Retrieval Helper
# ==================================================

def retrieve_chunks(query):
    results = collection.query(
        query_texts=[query],
        n_results=TOP_K
    )

    return (
        results["documents"][0],
        results["distances"][0],
        results["metadatas"][0]
    )


# ==================================================
# 9. Generate RAG Answer
# ==================================================

def generate_answer(query, retrieved_chunks, metadata):
    context = "\n\n".join(retrieved_chunks)

    sources = [
        {
            "source": meta["source"],
            "chunk_number": meta["chunk_number"]
        }
        for meta in metadata
    ]

    prompt = f"""
    You are an assistant answering questions based on provided documents.

    Follow these rules:

    1. Use only information supported by the provided context.
    2. Ignore any context that is irrelevant to the question.
    3. Do not use outside knowledge to fill in missing information.
    4. If the context does not contain enough information to answer the question, say:
    "I don't have enough information in the provided documents."
    5. Keep the answer concise and directly answer the question.

    Context:
    {context}

    Question:
    {query}

    Answer:
    """

    response = gen_client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt
    )

    return response.text, sources


# ==================================================
# 10. RAG Pipeline
# ==================================================

def rag_pipeline(query):
    retrieved_chunks, distances, metadata = retrieve_chunks(query)

    # Check relevance
    if distances[0] > RELEVANCE_THRESHOLD:
        return {
            "answer": "I don't have enough information in the provided documents.",
            "sources": [],
            "distances": []
        }

    # Generate answer
    answer, sources = generate_answer(
        query,
        retrieved_chunks,
        metadata
    )

    return {
        "answer": answer,
        "sources": sources,
    }


# ==================================================
# 11. Run RAG Pipeline
# ==================================================

query = input("Ask a question: ")

result = rag_pipeline(query)

answer = result["answer"]
sources = result["sources"]

# ==================================================
# 12. Display Final Answer
# ==================================================

print("\nAnswer:\n")
print(answer)

print("\nSources:\n")

for source in sources:
    print(f"Source: {source['source']}")
    print(f"Chunk: {source['chunk_number']}")


# ==================================================
# 13. Evaluate Retrieval
# ==================================================

def evaluate_retrieval():
    print("\n========== RAG EVALUATION ==========\n")

    for item in EVALUATION_QUESTIONS:

        question = item["question"]
        expected_relevant = item["relevant"]

        _, distances, _ = retrieve_chunks(question)

        best_distance = distances[0]

        actual_relevant = best_distance <= RELEVANCE_THRESHOLD

        passed = actual_relevant == expected_relevant

        print(f"Question: {question}")
        print(f"Best distance: {best_distance:.4f}")
        print(f"Expected relevant: {expected_relevant}")
        print(f"Actual relevant: {actual_relevant}")
        print(f"Result: {'PASS' if passed else 'FAIL'}")
        print()


# evaluate_retrieval()