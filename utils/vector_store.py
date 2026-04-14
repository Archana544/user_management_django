import os
import re
import numpy as np
from google import genai
import psycopg2
from psycopg2.extras import execute_values

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable is not set.")

client = genai.Client()


def get_db_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        database=os.getenv("DB_NAME", "ai_doc_platform"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", "postgres"),
        port=os.getenv("DB_PORT", "5432")
    )

def setup_vector_table():
    """
    Create the embeddings table if it doesn't exist.
    """
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")

    cur.execute("""
        CREATE TABLE IF NOT EXISTS document_chunks (
            id          SERIAL PRIMARY KEY,
            document_id INTEGER NOT NULL,
            chunk_text  TEXT NOT NULL,
            embedding   vector(768),
            created_at  TIMESTAMP DEFAULT NOW()
        );
    """)

    # IVFFlat index only works up to 2000 dims
    cur.execute("""
        CREATE INDEX IF NOT EXISTS chunks_embedding_idx
        ON document_chunks
        USING ivfflat (embedding vector_cosine_ops)
        WITH (lists = 100);
    """)

    conn.commit()
    cur.close()
    conn.close()

def clean_text(text: str) -> str:
    """
    Normalize spaces and fix common OCR/pdf extraction issues.
    """
    text = re.sub(r'\s+', ' ', text)  # collapse multiple spaces/newlines
    text = text.replace("DearPlease", "Dear Please")
    return text.strip()


def get_embedding(texts: list[str]) -> list[list[float]]:
    """
    Generate 768-dim embeddings using Gemini and slice to fit PostgreSQL column.
    """
    embeddings = []
    for text in texts:
        result = client.models.embed_content(
            model="gemini-embedding-001",
            contents=text
        )
        
        full_vec = result.embeddings[0].values

        vec_768 = [float(x) for x in full_vec[:768]]

        embeddings.append(vec_768)

    return embeddings

def chunk_text(text: str, chunk_size=150, overlap=30) -> list[str]:
    """
    Split text into overlapping chunks.
    """
    text = clean_text(text)  
    words = text.split()
    chunks = []
    i = 0
    while i < len(words):
        chunk = " ".join(words[i:i + chunk_size])
        chunks.append(chunk)
        i += chunk_size - overlap
    return chunks

def add_document_to_index(document_id: int, text: str):
    chunks = chunk_text(text)
    if not chunks:
        return

    embeddings = get_embedding(chunks)

    conn = get_db_connection()
    cur = conn.cursor()

    execute_values(
        cur,
        """
        INSERT INTO document_chunks
            (document_id, chunk_text, embedding)
        VALUES %s
        """,
        [(document_id, chunk, embedding) for chunk, embedding in zip(chunks, embeddings)]
    )

    conn.commit()
    cur.close()
    conn.close()

def search_similar_chunks(query: str, top_k=3, document_id: int = None) -> list[str]:
    print(f"[SEARCH] Searching for: {query}")

    query_embedding = get_embedding([query])[0]
    print(f"[SEARCH] Query embedding dims: {len(query_embedding)}")

    conn = get_db_connection()
    cur = conn.cursor()

    if document_id:
        cur.execute(
            "SELECT COUNT(*) FROM document_chunks WHERE document_id = %s",
            (document_id,)
        )
    else:
        cur.execute("SELECT COUNT(*) FROM document_chunks")
    total = cur.fetchone()[0]
    print(f"[SEARCH] Total chunks in DB: {total}")

    if total == 0:
        print("[SEARCH] No chunks in DB!")
        cur.close()
        conn.close()
        return []

    if document_id:
        cur.execute(
            """
            SELECT chunk_text,
                   embedding <=> %s::vector AS distance
            FROM document_chunks
            WHERE document_id = %s
            ORDER BY embedding <=> %s::vector
            LIMIT %s
            """,
            (query_embedding, document_id, query_embedding, top_k)
        )
    else:
        cur.execute(
            """
            SELECT chunk_text,
                   embedding <=> %s::vector AS distance
            FROM document_chunks
            ORDER BY embedding <=> %s::vector
            LIMIT %s
            """,
            (query_embedding, query_embedding, top_k)
        )

    rows = cur.fetchall()
    print(f"[SEARCH] Rows returned: {len(rows)}")
    for row in rows:
        print(f"[SEARCH] Distance: {row[1]:.4f} | Text: {row[0][:80]}")

    cur.close()
    conn.close()

    return [row[0] for row in rows]

def delete_document_chunks(document_id: int):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "DELETE FROM document_chunks WHERE document_id = %s",
        (document_id,)
    )
    conn.commit()
    cur.close()
    conn.close()



# import os
# import faiss
# import numpy as np
# from openai import OpenAI

# client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# dimension = 1536  
# index = faiss.IndexFlatL2(dimension)
# chunk_store = []
# doc_store = []


# def get_embedding(texts):
#     response = client.embeddings.create(
#         model="text-embedding-ada-002",
#         input=texts
#     )
#     return [item.embedding for item in response.data]


# def chunk_text(text, chunk_size=500):
#     words = text.split()
#     return [" ".join(words[i:i + chunk_size])
#             for i in range(0, len(words), chunk_size)]


# def add_document_to_index(document_id, text):
#     chunks = chunk_text(text)
#     embeddings = get_embedding(chunks)
#     index.add(np.array(embeddings).astype("float32"))
#     chunk_store.extend(chunks)
#     doc_store.extend([document_id] * len(chunks))


# def search_similar_chunks(query, top_k=3):
#     if index.ntotal == 0:
#         return []
#     query_embedding = get_embedding([query])[0]
#     distances, indices = index.search(
#         np.array([query_embedding]).astype("float32"), top_k
#     )
#     return [chunk_store[i] for i in indices[0] if 0 <= i < len(chunk_store)]