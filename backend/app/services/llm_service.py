import os
import httpx
import logging  
from dotenv import load_dotenv
from pathlib import Path
from app.models.models import TicketPriority


# Hide HTTPX / HTTPCore request logs
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)

logging.getLogger("httpx").disabled = True
logging.getLogger("httpcore").disabled = True
logger = logging.getLogger(__name__)



BASE_DIR = Path(__file__).resolve().parent
ENV_PATH = BASE_DIR / ".env"

print("ENV PATH:", ENV_PATH)
print("ENV EXISTS:", ENV_PATH.exists())


load_dotenv(ENV_PATH, override=True)

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

'''
print("================================")
print("ENV PATH:", ENV_PATH)
print("ENV EXISTS:", ENV_PATH.exists())
print("GOOGLE_API_KEY EXISTS:", bool(GOOGLE_API_KEY))
print("GOOGLE_API_KEY LENGTH:", len(GOOGLE_API_KEY) if GOOGLE_API_KEY else 0)
print("================================")
'''

LLM_MODEL = "gemini-3.6-flash"  
GOOGLE_API_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    f"{LLM_MODEL}:generateContent"
)




def build_prompt(complaint_text: str, category: str, sentiment: str, priority: str,
                  building_number: str, apartment_number: str) -> str:

    sentiment_note = ""

    if sentiment == "negative":
        sentiment_note = (
            "The customer appears frustrated or upset. "
            "Use an empathetic, calm, and reassuring tone."
        )

    prompt = f"""
    You are a professional customer service assistant for a Facility Management company.

    Complaint Information:
    - Customer complaint: "{complaint_text}"
    - Issue category: {category}
    - Building number: {building_number}
    - Apartment number: {apartment_number}
    - Customer sentiment: {sentiment}
    - Priority level: {priority}


    {sentiment_note}

    Your task:
1. Write a short and professional response to the customer, with a maximum of 3–4 sentences.
2. Acknowledge that the complaint has been received.
3. Clearly mention that the maintenance team responsible for "{category}" has been notified.
4. Take the priority level into account when writing the response.
5. Do not promise a specific resolution time unless a confirmed time is provided.
6. If the customer is upset, use an empathetic and reassuring tone.
7. Do not repeat unnecessary details such as the building or apartment number unless relevant.
8. Do not invent information that is not provided.
9. The response must be written entirely in English.
10. Use simple, natural, and conversational English that sounds appropriate when converted to speech.
11. Do not use bullet points, headings, emojis, or technical language.
12. Return only the customer-facing response.

    Response:
"""
    return prompt

async def generate_llm_response(complaint_text: str, category: str, sentiment: str, priority: str,
                                 building_number: str, apartment_number: str) -> str:
    
    
    prompt = build_prompt(complaint_text, category, sentiment, priority, building_number, apartment_number)


    headers = {
            "Content-Type": "application/json",
        }

    payload = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": prompt
                        }
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.4,
                "maxOutputTokens": 2000
            }
        }
    
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:

            response = await client.post(
                GOOGLE_API_URL,
                headers=headers,
                params={
                    "key": GOOGLE_API_KEY
                },
                json=payload
            )

            response.raise_for_status()

            data = response.json()
            #print("FULL GEMINI RESPONSE:")
            #print(data)

        # Extract generated text from Gemini response
        llm_text = (
            data["candidates"][0]["content"]["parts"][0]["text"]
        )
        #print("FULL LLM TEXT:")
        #print(repr(llm_text))
        return llm_text.strip()

    except httpx.HTTPStatusError as e:

        logger.error(
            f"Gemini API error: "
            f"{e.response.status_code} - {e.response.text}"
        )

        # Fallback response if Gemini API fails
        return (
            f"Your complaint regarding {category} has been received. "
            "Our maintenance team has been notified and will review your request."
        )

    except Exception as e:

        logger.error(
            f"Unexpected error while calling Gemini: {e}"
        )

        # Fallback response for unexpected errors
        return (
            f"Your complaint regarding {category} has been received. "
            "Our maintenance team has been notified and will review your request."
        )
        
        
        
        


import asyncio
    
import random

def determine_priority(category: str, sentiment: str, confidence: float, complaint_text: str) -> TicketPriority:
    """
    Determine the priority of a ticket based on its category.
    Adjust the logic as needed for your specific use case.
    """
    urgent_categories = { "Electricity Issue","Security Complaint",
                         "Plumbing Issue","Water Supply Request",}

    urgent_keywords = ["fire","smoke","electrical hazard","electric shock","gas leak",
                       "water leaking near electrical", "water leak near electrical",
                       "flooding", "flood","no electricity","power outage",
                       "elevator stuck", "emergency", "sparks","short circuit",]

    high_keywords = ["leaking","water leak","leakage","completely stopped",
                     "not working", "broken","dangerous","damage",
                     "very hot","no water",]

    text = complaint_text.lower()

    # 1. Immediate safety/emergency issues
    if any(keyword in text for keyword in urgent_keywords):
        return TicketPriority.URGENT

    # 2. Serious facility categories
    if category in urgent_categories:
        return TicketPriority.HIGH

    # 3. Serious wording in the complaint
    if any(keyword in text for keyword in high_keywords):
        return TicketPriority.HIGH

    # 4. Customer sentiment
    if sentiment == "negative":
        return TicketPriority.MEDIUM

    # 5. Low model confidence
    if confidence < 0.5:
        return TicketPriority.MEDIUM

    return TicketPriority.LOW


# Sentiment Analysis
#-------------------------------------------------------
async def get_sentiment_from_llm(text: str, max_retries: int = 3) -> str:
    prompt = f"""
Analyze the sentiment of the following facility management complaint.

Return ONLY one word:
positive
negative
neutral

Complaint:
{text}
"""

    payload = {
        "contents": [
            {"parts": [{"text": prompt}]}
        ],
        "generationConfig": {
            "temperature": 0,
            "maxOutputTokens": 200
        }
    }

    valid_sentiments = {"positive", "negative", "neutral"}

    for attempt in range(max_retries):
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    GOOGLE_API_URL,
                    params={"key": GOOGLE_API_KEY},
                    json=payload
                )

            # لو 503 أو 429 (rate limit) نعيد المحاولة بدل ما نستسلم فوراً
            if response.status_code in (503, 429):
                wait_time = (2 ** attempt) + random.uniform(0, 1)
                logger.warning(
                    f"Gemini overloaded ({response.status_code}), "
                    f"retry {attempt + 1}/{max_retries} after {wait_time:.1f}s"
                )
                await asyncio.sleep(wait_time)
                continue

            response.raise_for_status()
            data = response.json()

            candidates = data.get("candidates", [])
            if not candidates:
                logger.warning("Gemini returned no candidates")
                return "neutral"

            parts = candidates[0].get("content", {}).get("parts", [])
            if not parts:
                logger.warning("Gemini returned no parts")
                return "neutral"

            sentiment_raw = parts[0].get("text", "").strip().lower()

            if sentiment_raw not in valid_sentiments:
                logger.warning(f"Unexpected sentiment value from Gemini: {sentiment_raw!r}")
                return "neutral"

            return sentiment_raw

        except httpx.HTTPStatusError as e:
            logger.error(
                f"Gemini sentiment API error: {e.response.status_code} - {e.response.text}"
            )
            # لو خطأ مو 503/429 (مثلاً 400 أو 401) ما فيه فايدة نعيد المحاولة
            if e.response.status_code not in (503, 429):
                return "neutral"

        except Exception as e:
            logger.error(f"Error during Gemini sentiment analysis: {e}")
            return "neutral"

    logger.error("Gemini sentiment analysis failed after all retries — defaulting to neutral")
    return "neutral"
