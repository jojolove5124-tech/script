from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import os

app = FastAPI()

# Разрешаем запросы из Roblox и любых других источников
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# API-ключ из переменных окружения Render
TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY", "")
TOGETHER_API_URL = "https://api.together.xyz/v1/chat/completions"

class AIRequest(BaseModel):
    prompt: str
    model: str = "deepseek-ai/DeepSeek-V3"

@app.get("/")
def root():
    return {"status": "AI сервер работает!"}

@app.get("/ping")
def ping():
    return {"status": "alive"}

@app.post("/ai")
async def get_ai_response(req: AIRequest):
    if not TOGETHER_API_KEY:
        return {"error": "API ключ не настроен. Добавьте TOGETHER_API_KEY в переменные окружения Render."}
    
    headers = {
        "Authorization": f"Bearer {TOGETHER_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": req.model,
        "messages": [{"role": "user", "content": req.prompt}],
        "temperature": 0.7,
        "max_tokens": 1000
    }
    
    try:
        response = requests.post(TOGETHER_API_URL, json=payload, headers=headers, timeout=30)
        if response.status_code != 200:
            return {"error": f"Ошибка API: {response.status_code}"}
        data = response.json()
        reply = data["choices"][0]["message"]["content"]
        return {"response": reply}
    except Exception as e:
        return {"error": str(e)}
