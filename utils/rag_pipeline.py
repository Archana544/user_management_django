def build_rag_prompt(question, context_list):
    """
    Builds a structured RAG prompt with guardrails, citations, and evaluation-friendly output.
    """
    top_k = 3
    selected_chunks = context_list[:top_k]

    # Structured context with chunk IDs
    context = "\n\n".join(
        [f"[Chunk {i+1}]: {chunk}" for i, chunk in enumerate(selected_chunks)]
    )

    prompt = f"""
You are an expert AI assistant specialized in factual, context-based question answering.

ROLE:
- You answer questions strictly based on provided context.
- You do NOT rely on external or prior knowledge.

INSTRUCTIONS:
1. Read the question carefully.
2. Analyze the provided context chunks.
3. Extract the most relevant information.
4. If the answer is not explicitly present, respond with: "I don't know".
5. Do NOT infer, assume, or hallucinate.
6. Keep the answer concise and accurate.

CONTEXT:
{context}

QUESTION:
{question}

OUTPUT FORMAT:
Answer: <clear and concise answer>
Sources: <comma-separated chunk numbers used, e.g., 1,3>
Confidence: <High / Medium / Low>

RULES:
- Only use the provided context
- No external knowledge
- No fabrication
- Cite only relevant chunks
- If unsure → "I don't know"

BEGIN ANSWER:
"""

    return prompt.strip()