def build_rag_prompt(question, context_list):

    context = "\n".join(context_list)

    prompt = f"""
You are a precise question answering AI.

Extract the answer from the context.

Question: {question}

Context:
{context}


Answer:
"""

    return prompt.strip()