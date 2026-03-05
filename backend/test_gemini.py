import asyncio
from app.services.gemini_service import classify_questions

async def main():
    questions = [{
        "question_text": "What is the capital of India?",
        "options": [{"option_text": "Delhi"}, {"option_text": "Mumbai"}]
    }]
    res = await classify_questions(questions)
    print("Result:", res)

asyncio.run(main())
