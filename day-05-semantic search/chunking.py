import re


text = """
FastAPI is a modern Python framework for building APIs.
It supports automatic API documentation.
You can define request and response models using Pydantic.
Authentication can be implemented using OAuth2 and JWT tokens.
FastAPI applications can be deployed using Docker.
PostgreSQL can be used as the application's database.
"""


chunk_size = 100


def split_into_chunks(text, chunk_size):
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())

    chunks = []
    current_chunk = []
    current_length = 0

    for sentence in sentences:

        if current_length + len(sentence) <= chunk_size:
            current_chunk.append(sentence)
            current_length += len(sentence) + 1

        else:
            chunks.append(" ".join(current_chunk))

            # Keep the last sentence as overlap
            current_chunk = [current_chunk[-1], sentence]
            current_length = len(current_chunk[-1]) + len(sentence) + 2

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks


chunks = split_into_chunks(text, chunk_size)


for i, chunk in enumerate(chunks):
    print(f"\nChunk {i + 1}:")
    print(chunk)