from google import  genai

from config import GEMINI_API_KEY, MODEL_NAME


client = genai.Client(
    api_key=GEMINI_API_KEY
)

history = []

def ask_gemini(question: str) -> str:
    
    history.append({
        "role": "user",
        "parts": [{"text": question}]
    })

    response = client.models.generate_content(
        model=MODEL_NAME, 
        contents=history
    )

    answer = response.text

    history.append({
        "role": "model",
        "parts": [{"text": answer}]
    })
    
    return answer