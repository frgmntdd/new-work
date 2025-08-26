import os
import asyncio
from typing import Optional, Dict, Any, List


from fastapi import FastAPI, Request, Header, HTTPException
import httpx


# Google GenAI SDK
from google import genai
from google.genai.types import (
GenerateContentConfig,
)


# === Конфигурация из переменных окружения ===
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
TELEGRAM_WEBHOOK_SECRET = os.getenv("TELEGRAM_WEBHOOK_SECRET") # тот же, что передадите в setWebhook
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-pro")


if not TELEGRAM_BOT_TOKEN:
raise RuntimeError("TELEGRAM_BOT_TOKEN is not set")
if not GEMINI_API_KEY:
raise RuntimeError("GEMINI_API_KEY is not set")


# === Инициализация клиентов ===
app = FastAPI(title="Gemini 2.5 Pro Telegram Bot")


# Асинхронный клиент Gemini
_genai_client = genai.Client(api_key=GEMINI_API_KEY)


# Память сессий: chat_id -> chat session
SESSIONS: Dict[int, Any] = {}


# Телеграм API endpoint
TELEGRAM_API = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"




async def tg_send_message(chat_id: int, text: str, reply_to_message_id: Optional[int] = None):
"""Отправка текстового сообщения в Telegram с безопасным разбиением по лимиту 4096 символов."""
MAX = 3800 # запас, чтобы не упереться в лимит
chunks: List[str] = [text[i:i+MAX] for i in range(0, len(text), MAX)] or [text]


async with httpx.AsyncClient(timeout=30) as http:
for chunk in chunks:
payload = {
"chat_id": chat_id,
"text": chunk,
"disable_web_page_preview": True,
}
if reply_to_message_id:
payload["reply_to_message_id"] = reply_to_message_id
# только к первому сообщению привяжем как reply
reply_to_message_id = None
await http.post(f"{TELEGRAM_API}/sendMessage", data=payload)




async def get_or_create_chat_session(chat_id: int):
chat = SESSIONS.get(chat_id)
if chat is None:
# system_instruction задаёт поведение бота на всю беседу
chat = await _genai_client.aio.chats.create(
model=GEMINI_MODEL,
config=GenerateContentConfig(
system_instruction=(
"Ты — дружелюбный Telegram‑ассистент на базе Gemini 2.5 Pro. "
print("Gemini error:", repr(e))