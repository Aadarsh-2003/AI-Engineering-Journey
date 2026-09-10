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


# ==================================================
# 2. Configuration
# ==================================================

CHUNK_SIZE = 100
TOP_K = 3
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
COLLECTION_NAME = "document_chunks"


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
# 8. Retrieve Relevant Chunks
# ==================================================

query = input("Ask a question: ")

results = collection.query(
    query_texts=[query],
    n_results=TOP_K
)

retrieved_chunks = results["documents"][0]
distances = results["distances"][0]
metadata = results["metadatas"][0]


# ==================================================
# 9. Display Retrieved Chunks
# ==================================================

print("\nRelevant chunks:\n")

for document, distance, meta in zip(
    retrieved_chunks,
    distances,
    metadata
):
    print(f"Distance: {distance:.4f}")
    print(f"Chunk: {document}")
    print(f"Metadata: {meta}")
    print()


# ==================================================
# 10. Generate RAG Answer
# ==================================================

def generate_answer(query, retrieved_chunks):
    context = "\n\n".join(retrieved_chunks)

    prompt = f"""
You are an assistant answering questions based on provided documents.

Use only the information in the context below.

If the answer is not present in the context, say:
"I don't have enough information in the provided documents."

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

    return response.text


answer = generate_answer(
    query,
    retrieved_chunks
)


# ==================================================
# 11. Display Final Answer
# ==================================================

print("\nAnswer:\n")
print(answer)

