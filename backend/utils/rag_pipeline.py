import chromadb
from langchain.text_splitter import RecursiveCharacterTextSplitter
import openai
import os

openai.api_key = os.getenv("OPENAI_API_KEY")

# Vector DB
client = chromadb.Client()
collection = client.get_or_create_collection(name="documents")


def chunk_text(text):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )

    return splitter.split_text(text)


def generate_embedding(text):
    response = openai.Embedding.create(
        model="text-embedding-ada-002",
        input=text
    )

    return response["data"][0]["embedding"]


def index_document(document_id, extracted_text):

    chunks = chunk_text(extracted_text)

    for i, chunk in enumerate(chunks):

        embedding = generate_embedding(chunk)

        collection.add(
            embeddings=[embedding],
            documents=[chunk],
            ids=[f"{document_id}_{i}"]
        )

def retrieve_relevant_context(query, top_k=3):

    query_embedding = generate_embedding(query)

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )

    if results["documents"]:
        return "\n".join(results["documents"][0])

    return ""