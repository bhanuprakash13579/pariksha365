import fitz # PyMuPDF
import os
import io
import json
import asyncio
from PIL import Image
from typing import List, Dict, Any
from fastapi import UploadFile
from app.core.config import settings

UPLOAD_DIR = "app/static/uploads/images"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def parse_raw_text_to_questions(text_blob: str) -> List[Dict[str, Any]]:
    import re
    # More robust regex handling potential HTML tags if pasted directly from web
    import html
    text_blob = html.unescape(text_blob)
    
    question_pattern = re.compile(r'^(?:<[^>]+>)*(?:Q|Ques|Question)?\s*\.?\s*(\d+)[\.\)]?\s*(.*)', re.IGNORECASE)
    option_pattern = re.compile(r'^(?:<[^>]+>)*\s*[\(\[]?([A-D1-4])[\]\)\.]\s*(.*)', re.IGNORECASE)
    solution_pattern = re.compile(r'^(?:<[^>]+>)*(?:Solutions?|Explanations?|Correct Answers?|Correct Options?|Answers?|Ans|Hints?|Check Solution)\b\s*[:\-\.]?\s*(.*)', re.IGNORECASE)
    
    current_question = None
    all_questions = []
    
    # Strip simple HTML block tags for splitting if pasted from rich text
    clean_blob = re.sub(r'</?(?:p|div|br|li|ul|ol|table|tr|td|th)[^>]*>', '\n', text_blob)
    clean_blob = re.sub(r'<[^>]+>', '', clean_blob) # strip inline tags
    
    lines = [line.strip() for line in clean_blob.split('\n') if line.strip()]
    
    parsing_mode = 'question'
    
    for text in lines:
        q_match = question_pattern.match(text)
        if q_match:
             if current_question:
                 all_questions.append(current_question)
             current_question = {
                 "question_text": text,
                 "image_url": None,
                 "explanation": "",
                 "difficulty": "MEDIUM",
                 "options": []
             }
             parsing_mode = 'question'
             continue
             
        s_match = solution_pattern.match(text)
        if s_match and current_question:
             parsing_mode = 'solution'
             solution_content = s_match.group(1).strip()
             if solution_content:
                 current_question["explanation"] += f"{solution_content}\n"
             continue
            
        o_match = option_pattern.match(text)
        if o_match and current_question and parsing_mode != 'solution':
             current_question["options"].append({
                 "option_text": text,
                 "is_correct": False
             })
             parsing_mode = 'options'
             continue
            
        if current_question:
             if parsing_mode == 'solution':
                 current_question["explanation"] += f"{text}\n"
             elif parsing_mode == 'options' and len(current_question["options"]) > 0:
                 current_question["options"][-1]["option_text"] += f" {text}"
             else:
                 current_question["question_text"] += f"\n{text}"

    if current_question:
        all_questions.append(current_question)
    return all_questions

async def extract_from_raw_text(text: str) -> List[Dict[str, Any]]:
    """Entrypoint for the raw HTML/Text Paste UI functionality."""
    return parse_raw_text_to_questions(text)

async def extract_text_and_images(file: UploadFile, ai_model: str = "gemini") -> List[Dict[str, Any]]:
    """
    Parses a PDF by converting each page to an image and sending it to either 
    Gemini Vision or ChatGPT Vision for structured JSON extraction of English questions.
    """
    import google.generativeai as genai
    from openai import OpenAI
    import base64

    # Setup Clients
    gemini_model = None
    openai_client = None
    
    if ai_model == "gemini":
        if not settings.GEMINI_API_KEY:
            print("GEMINI_API_KEY not set. Cannot use Gemini Vision.")
            return []
        genai.configure(api_key=settings.GEMINI_API_KEY)
        gemini_model = genai.GenerativeModel("gemini-3-flash")
    elif ai_model == "chatgpt":
        if not settings.OPENAI_API_KEY:
            print("OPENAI_API_KEY not set. Cannot use ChatGPT Vision.")
            return []
        openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)
    
    pdf_bytes = await file.read()
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    
    all_questions = []
    
    # Precise OCR JSON extractor prompt
    prompt = """You are an OCR and data extraction expert for Indian competitive exams.
Below is an image of an exam paper page, which might contain both Hindi and English text side-by-side or interleaved.

Your task is to extract ONLY the English questions and their options. Completely ignore the Hindi translations.
If the entire question is in English, extract it.

Return ONLY a valid structured JSON array of objects. Do NOT wrap the output in markdown blocks (e.g. no ```json). Start your response exactly with [ and end exactly with ].
Do not include any conversational text.
Each object in the array must have exactly the following structure:
[
  {
    "question_text": "The full text of the question, including the question number if present",
    "image_url": null,
    "explanation": "",
    "difficulty": "MEDIUM",
    "options": [
      {
        "option_text": "(A) Text of first option",
        "is_correct": false
      },
      {
        "option_text": "(B) Text of second option",
        "is_correct": false
      }
    ]
  }
]

If no questions are found on this page, return an empty array []"""

    for page_num in range(len(doc)):
        try:
            # Render page to an image
            page = doc[page_num]
            pix = page.get_pixmap(dpi=150)
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            
            response_text = ""
            
            if ai_model == "gemini" and gemini_model:
                # Gemini Payload
                response = gemini_model.generate_content([prompt, img])
                response_text = response.text.strip()
                
            elif ai_model == "chatgpt" and openai_client:
                # OpenAI Payload (Base64 JPEG)
                buffered = io.BytesIO()
                img.save(buffered, format="JPEG")
                img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
                
                response = openai_client.chat.completions.create(
                    model="gpt-4o", # Can be updated to gpt-4o or latest vision model
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": prompt},
                                {
                                    "type": "image_url",
                                    "image_url": {"url": f"data:image/jpeg;base64,{img_str}"},
                                }
                            ],
                        }
                    ],
                    max_tokens=4000,
                )
                response_text = response.choices[0].message.content.strip()
            
            # Clean up potential markdown fences and grab just the JSON array
            import re
            
            # Find everything between [ and the last ]
            json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
            
            if not json_match:
                continue
                
            json_string = json_match.group(0)
            
            if json_string == "[]":
                continue
                
            page_questions = json.loads(json_string)
            if isinstance(page_questions, list):
                all_questions.extend(page_questions)
                
            # Rate limiting sleep just in case
            if page_num < len(doc) - 1:
                await asyncio.sleep(1.5)
                
        except Exception as e:
            print(f"[{ai_model.upper()} OCR] Failed to process page {page_num}: {e}")
            continue

    if ai_model == "tesseract":
        import pytesseract
        for page_num in range(len(doc)):
            try:
                page = doc[page_num]
                pix = page.get_pixmap(dpi=300)
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                
                try:
                    text_blob = pytesseract.image_to_string(img, lang="eng+hin")
                except pytesseract.TesseractNotFoundError:
                    print("Tesseract binary not installed on the system.")
                    break
                    
                page_questions = parse_raw_text_to_questions(text_blob)
                all_questions.extend(page_questions)

            except Exception as e:
                 print(f"[TESSERACT OCR] Failed page {page_num}: {e}")
                 
    elif ai_model == "pymupdf":
        for page_num in range(len(doc)):
            try:
                page = doc[page_num]
                text_blob = page.get_text()
                page_questions = parse_raw_text_to_questions(text_blob)
                all_questions.extend(page_questions)
            except Exception as e:
                 print(f"[PYMUPDF TXT] Failed page {page_num}: {e}")

    return all_questions
