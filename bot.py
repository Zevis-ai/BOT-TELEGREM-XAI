from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import json
import aiohttp
import nest_asyncio
import asyncio
from dotenv import load_dotenv
import os

# מאפשר הרצת לולאות אירועים מקוננות
nest_asyncio.apply()

# קרא טוקנים מקובץ חיצוני או משתני סביבה
load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
XAI_API_KEY = os.getenv("XAI_API_KEY")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("שלום! אני בוט AI. איך אוכל לעזור לך?")

async def get_xai_response(message: str) -> str:
    async with aiohttp.ClientSession() as session:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {XAI_API_KEY}"
        }
        
        payload = {
            "messages": [
                {
                    "role": "system",
                    "content": "You are a helpful assistant."
                },
                {
                    "role": "user",
                    "content": message
                }
            ],
            "model": "grok-beta",
            "stream": False,
            "temperature": 0.7
        }
        
        try:
            async with session.post("https://api.x.ai/v1/chat/completions", 
                                headers=headers, 
                                json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    return data['choices'][0]['message']['content']
                return "מצטער, אירעה שגיאה בקבלת התשובה."
        except Exception as e:
            return f"אירעה שגיאה: {str(e)}"

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    response = await get_xai_response(user_message)
    await update.message.reply_text(response)

def main():
    # יצירת אפליקציה
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # הוספת handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # הפעלת הבוט
    print("הבוט מתחיל לרוץ...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main() 