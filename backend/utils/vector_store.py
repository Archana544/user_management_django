import os
import faiss
import numpy as np
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

dimension = 1536  
index = faiss.IndexFlatL2(dimension)
chunk_store = []
doc_store = []


def get_embedding(texts):
    response = client.embeddings.create(
        model="text-embedding-ada-002",
        input=texts
    )
    return [item.embedding for item in response.data]


def chunk_text(text, chunk_size=500):
    words = text.split()
    return [" ".join(words[i:i + chunk_size])
            for i in range(0, len(words), chunk_size)]


def add_document_to_index(document_id, text):
    chunks = chunk_text(text)
    embeddings = get_embedding(chunks)
    index.add(np.array(embeddings).astype("float32"))
    chunk_store.extend(chunks)
    doc_store.extend([document_id] * len(chunks))


def search_similar_chunks(query, top_k=3):
    if index.ntotal == 0:
        return []
    query_embedding = get_embedding([query])[0]
    distances, indices = index.search(
        np.array([query_embedding]).astype("float32"), top_k
    )
    return [chunk_store[i] for i in indices[0] if 0 <= i < len(chunk_store)]