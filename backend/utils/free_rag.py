import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from utils.embedding import generate_embedding
from user_service.models import Document


def retrieve_relevant_context(query, top_k=3):

    query_vector = np.array(generate_embedding(query)).reshape(1, -1)

    docs = Document.objects.exclude(extracted_content__isnull=True)

    scored_docs = []

    for doc in docs:

        doc_vector = np.array(generate_embedding(doc.extracted_content)).reshape(1, -1)

        score = cosine_similarity(query_vector, doc_vector)[0][0]

        scored_docs.append((score, doc.extracted_content))

    scored_docs.sort(reverse=True)

    return "\n".join([d[1] for d in scored_docs[:top_k]])