"""
Gemini AI Service — Used ONLY at question ingestion time.
Classifies each question with subject, topic, difficulty, and explanation.
After tagging, the app runs entirely on its own — zero ongoing AI cost.
"""
import json
import asyncio
from typing import List, Dict, Any
from app.core.config import settings

# Pre-defined subject taxonomy for Indian competitive exams
VALID_SUBJECTS = [
    "Polity", "History", "Geography", "Economics", "General Science",
    "Physics", "Chemistry", "Biology", "English", "Reasoning",
    "Quantitative Aptitude", "Computer Knowledge", "Current Affairs",
    "Environmental Science", "General Knowledge", "Indian Culture",
    "International Relations", "Ethics", "Essay", "Hindi"
]

async def classify_questions(questions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Takes raw scraped questions and classifies them using Gemini AI.
    Returns the same list with subject, topic, difficulty, and explanation filled in.
    
    Processes in batches of 5 to stay within rate limits.
    """
    if not settings.OPENAI_API_KEY:
        print("[AI] No OPENAI_API_KEY set. Returning unclassified.")
        return questions
    
    try:
        from openai import OpenAI
        client = OpenAI(api_key=settings.OPENAI_API_KEY)
    except Exception as e:
        print(f"[AI] Failed to initialize OpenAI: {e}")
        return questions
    
    BATCH_SIZE = 5
    classified = []
    
    for i in range(0, len(questions), BATCH_SIZE):
        batch = questions[i:i + BATCH_SIZE]
        
        # Build the prompt
        batch_text = []
        for idx, q in enumerate(batch):
            options_text = ""
            if q.get("options"):
                for j, opt in enumerate(q["options"]):
                    label = chr(65 + j)  # A, B, C, D
                    opt_text = opt.get("option_text", "")
                    options_text += f"\n  ({label}) {opt_text}"
            
            batch_text.append(f"Q{idx + 1}: {q.get('question_text', '')}{options_text}")
        
        prompt = f"""You are an expert in Indian competitive exams (SSC, UPSC, Banking, Railway, etc.).

For each question below, classify it and return a JSON array with one object per question.

Each object MUST have exactly these fields:
- "subject": One of: {json.dumps(VALID_SUBJECTS)}
- "topic": A specific sub-topic within the subject (e.g., "Fundamental Rights", "Trigonometry", "Syllogism", "Indian Rivers", "Parts of Speech")
- "difficulty": One of "EASY", "MEDIUM", "HARD"
- "explanation": A brief 1-2 line explanation of the correct answer
- "correct_option_index": Your best guess for the correct answer (0-based index, 0=A, 1=B, 2=C, 3=D). Use -1 if unsure.

IMPORTANT: Return ONLY the raw JSON array. No markdown, no code fences, no extra text.

Questions:
{chr(10).join(batch_text)}"""
        
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2000
            )
            response_text = response.choices[0].message.content.strip()
            
            # Clean up potential markdown fences and grab just the JSON array
            import re
            
            # Find everything between [ and the last ]
            json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
            
            if not json_match:
                print(f"[AI] Failed to find JSON array in response: {response_text}")
                classifications = []
            else:
                json_string = json_match.group(0)
                if json_string == "[]":
                    classifications = []
                else:
                    classifications = json.loads(json_string)
            
            for idx, q in enumerate(batch):
                if idx < len(classifications):
                    c = classifications[idx]
                    q["subject"] = c.get("subject", "General Knowledge")
                    q["topic"] = c.get("topic", "General")
                    q["difficulty"] = c.get("difficulty", "MEDIUM")
                    q["explanation"] = c.get("explanation", "")
                    
                    # Auto-mark correct option if Gemini is confident
                    correct_idx = c.get("correct_option_index", -1)
                    if isinstance(correct_idx, int) and 0 <= correct_idx < len(q.get("options", [])):
                        for j, opt in enumerate(q["options"]):
                            opt["is_correct"] = (j == correct_idx)
                
                classified.append(q)
                
        except Exception as e:
            print(f"[AI] Batch {i // BATCH_SIZE} failed: {e}")
            # On failure, add questions without classification
            classified.extend(batch)
        
        # Rate limiting: 1 second between batches
        if i + BATCH_SIZE < len(questions):
            await asyncio.sleep(1)
    
    return classified
