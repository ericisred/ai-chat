from google import  genai

from config import GEMINI_API_KEY, MODEL_NAME


client = genai.Client(
    api_key=GEMINI_API_KEY
)

history = []

def ask_gemini_stream(question: str) -> str:
    
    history.append({
        "role": "user",
        "parts": [{"text": question}]
    })

    response = client.models.generate_content_stream(
        model=MODEL_NAME, 
        contents=history
    )

    full_answer = ""

    for chunk in response:
        if chunk.text:
            full_answer += chunk.text
            yield chunk.text

    history.append({
        "role": "model",
        "parts": [{"text": full_answer}]
    })
