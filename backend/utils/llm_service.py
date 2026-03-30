from google import genai
import os

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable is not set.")

client = genai.Client()

print("Available Gemini models:")
available_models = client.models.list()
for m in available_models:
    print(f"- {m.name} | description: {getattr(m, 'description', 'N/A')} | version: {getattr(m, 'version', 'N/A')}")

def generate_answer(prompt: str) -> str:
    try:
        print(f"[LLM] Sending prompt to Gemini...")

        response = client.models.generate_content(
            model="gemini-3.1-flash-lite-preview",
            contents=[prompt],  
            config=genai.types.GenerateContentConfig(
                temperature=0.2,
                max_output_tokens=1000
            )
        )

        if hasattr(response, "text"):
            answer = response.text
        elif hasattr(response, "content") and len(response.content) > 0:
            answer = response.content[0].text
        else:
            answer = ""

        answer = answer.strip()
        print(f"[LLM] Gemini response: {answer[:200]}")
        return answer if answer else "I don't know"

    except Exception as e:
        print(f"[LLM] Gemini error: {str(e)}")
        return "I don't know"