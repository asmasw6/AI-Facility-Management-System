import os
import httpx
import logging  
from dotenv import load_dotenv
from pathlib import Path
from app.models.models import TicketPriority
import asyncio
import random

import json
import re


# Hide HTTPX / HTTPCore request logs
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)

logging.getLogger("httpx").disabled = True
logging.getLogger("httpcore").disabled = True
logger = logging.getLogger(__name__)


BASE_DIR = Path(__file__).resolve().parent
ENV_PATH = BASE_DIR / ".env"
load_dotenv(ENV_PATH, override=True)

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
LLM_MODEL = "gemini-3.6-flash"  
GOOGLE_API_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    f"{LLM_MODEL}:generateContent"
)
BASE_DIR = Path(__file__).resolve().parents[2]
ENV_PATH = BASE_DIR / ".env"

print("Current file:", Path(__file__).resolve())
print("Calculated backend path:", BASE_DIR)
print("Looking for .env at:", ENV_PATH)
print("File exists:", ENV_PATH.is_file())

load_dotenv(ENV_PATH, override=True)

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
print("API key loaded:", bool(GOOGLE_API_KEY))

'''
print("ENV PATH:", ENV_PATH)
print("ENV EXISTS:", ENV_PATH.exists())

print("================================")
print("ENV PATH:", ENV_PATH)
print("ENV EXISTS:", ENV_PATH.exists())
print("GOOGLE_API_KEY EXISTS:", bool(GOOGLE_API_KEY))
print("GOOGLE_API_KEY LENGTH:", len(GOOGLE_API_KEY) if GOOGLE_API_KEY else 0)
print("================================")
'''

def build_prompt(complaint_text: str, category: str, sentiment: str, priority: str, customer_name: str,
                  building_number: str, apartment_number: str, language:str) -> str:

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
- Issue category: "{category}"
- Customer name: "{customer_name}"
- Building number: "{building_number}"
- Apartment number: "{apartment_number}"
- Customer sentiment: "{sentiment}"
- Priority level: "{priority}"

{sentiment_note}

Your task is to write ONLY the customer-facing response.

STRICT REQUIREMENTS:
1. You MUST address the customer using this exact name: "{customer_name}".
2. You MUST mention the building number "{building_number}".
3. You MUST mention the apartment number "{apartment_number}".
4. You MUST confirm that the complaint has been received.
5. You MUST state that the "{category}" maintenance team has been notified.
6. The response must reflect the "{priority}" priority level.
7. If the customer is upset, use an empathetic and reassuring tone.
8. Do NOT invent, change, or omit the customer name, building number, or apartment number.
9. Do NOT mention information that is not provided.
10. Do not promise a specific resolution time.
11. Write exactly 3-4 sentences.
12. Write entirely in the specified language: "{language}".
13. Use simple, natural, conversational English.
14. Do not use bullet points, headings, emojis, or technical language.
15. Return ONLY the customer-facing response.

The response MUST contain:
- Customer name: {customer_name}
- Building: {building_number}
- Apartment: {apartment_number}

Response:
    """
    return prompt




async def generate_llm_response(complaint_text: str, category: str, sentiment: str, priority: str,
                                 customer_name: str, building_number: str, apartment_number: str, language:str) -> str:
    
    
    prompt = build_prompt(complaint_text, category, sentiment, priority, customer_name, building_number, apartment_number, language)


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
        
        
        
# Priority
#---------------------------------------------------------------
# ---------- Keywords ------------ 
urgent_keywords = [
    # --- English ---
    "fire", "smoke", "electrical hazard", "electric shock", "gas leak",
    "water leaking near electrical", "water leak near electrical",
    "flooding", "flood", "no electricity", "power outage",
    "elevator stuck", "emergency", "sparks", "short circuit",
    # --- Arabic ---
    "حريق", "حرائق", "رائحة حريق", "دخان", "شرار", "ماس كهربائي", "تماس كهربائي",
    "صعقة", "صعق", "خطر كهربائي", "تسرب غاز", "تسريب غاز", "رائحة غاز",
    "تسرب مياه قرب الكهرباء", "تسريب مياه قرب الكهرباء", "تسرب مياه بالقرب من الكهرباء",
    "فيضان", "غرق", "غرقت", "يغمر", "تغمر", "غمر",
    "لا يوجد كهرباء", "لا توجد كهرباء", "ما فيه كهرباء", "بدون كهرباء",
    "انقطاع الكهرباء", "انقطاع التيار", "الكهرباء مقطوعة", "انقطعت الكهرباء",
    "المصعد عالق", "عالقين في المصعد", "علقت في المصعد", "المصعد متوقف بين",
    "طارئ", "طارئة", "طوارئ",
]

high_keywords = [
    # --- English ---
    "leaking", "water leak", "leakage", "completely stopped",
    "not working", "broken", "dangerous", "damage",
    "very hot", "no water",
    # --- Arabic ---
    "تسرب", "تسريب", "يسرب", "تسربت",
    "توقف تماما", "متوقف تماما", "توقفت تماما", "معطل تماما", "متعطل تماما",
    "لا يعمل", "لا تعمل", "ما يعمل", "ما تعمل", "لا يشتغل", "لا تشتغل",
    "ما يشتغل", "ما تشتغل", "مو شغال", "خربان", "عطل", "معطل", "متعطل",
    "مكسور", "انكسر", "مخلوع", "تالف",
    "خطر", "خطير",
    "ضرر", "اضرار",
    "حار جدا", "حر شديد", "حر جدا", "ساخن جدا",
    "لا يوجد ماء", "لا يوجد مياه", "لا توجد مياه", "ما فيه ماء", "ما فيه مياه",
    "بدون ماء", "بدون مياه", "انقطاع المياه", "انقطاع الماء",
    "المياه مقطوعة", "الماء مقطوع",
]

# Categories that are serious by nature (edit to match your policy).
HIGH_PRIORITY_CATEGORIES = {
    "Security Complaint", "Electricity Issue", "Water Supply Request",
    "شكوى أمنية", "مشكلة كهرباء", "طلب إمداد المياه",
}

NEGATIVE_SENTIMENTS = {"negative", "سلبي"}
_DIACRITICS = re.compile(r"[\u0610-\u061A\u064B-\u065F\u0670\u06D6-\u06ED]")


def _norm(text: str) -> str:
    """Lowercase + unify Arabic letters. English text stays the same."""
    text = str(text).lower()
    text = _DIACRITICS.sub("", text).replace("\u0640", "")
    text = re.sub("[إأآٱ]", "ا", text)
    text = text.replace("ى", "ي").replace("ة", "ه").replace("ؤ", "و").replace("ئ", "ي")
    return re.sub(r"\s+", " ", text).strip()


URGENT_NORM = [_norm(k) for k in urgent_keywords]
HIGH_NORM = [_norm(k) for k in high_keywords]


def contains_keyword(text: str, keywords_norm: list[str]) -> bool:
    t = _norm(text)
    return any(k in t for k in keywords_norm)


def determine_priority(category: str, sentiment: str, confidence: float, complaint_text: str) -> TicketPriority:
   
    # 1. Immediate safety/emergency issues
    if contains_keyword(complaint_text, URGENT_NORM):
        return TicketPriority.URGENT

    # 2. Serious facility categories
    if category in HIGH_PRIORITY_CATEGORIES:
        return TicketPriority.HIGH

    # 3. Serious wording in the complaint
    if contains_keyword(complaint_text, HIGH_NORM):
        return TicketPriority.HIGH

    # 4. Customer sentiment
    if sentiment in NEGATIVE_SENTIMENTS:
        return TicketPriority.MEDIUM

    # 5. Low model confidence
    if confidence < 50:
        return TicketPriority.MEDIUM

    return TicketPriority.LOW
 
'''
def determine_priority(category: str, sentiment: str, confidence: float, complaint_text: str) -> TicketPriority:
    """
    Determine the priority of a ticket based on its category.
    Adjust the logic as needed for your specific use case.
    """
    urgent_categories = {
    # English labels
    "Air Conditioning","Garbage Collection", "Security Complaint","Water Supply Request",
    "Maintenance Request","Cleaning Request","Plumbing Issue",
    "Electricity Issue", "Pest Control","General Inquiry",

    # Arabic labels
    "التكييف والتبريد","جمع النفايات","شكوى أمنية","طلب إمداد المياه", "طلب صيانة","طلب نظافة",
    "مشكلة سباكة","مشكلة كهرباء","مكافحة الحشرات","استفسار عام",}

    urgent_keywords = ["fire","smoke","electrical hazard","electric shock","gas leak",
                       "water leaking near electrical", "water leak near electrical",
                       "flooding", "flood","no electricity","power outage",
                       "elevator stuck", "emergency", "sparks","short circuit",
                        # --- Arabic ---
                        "حريق", "حرائق", "رائحة حريق", "دخان", "شرار", "ماس كهربائي", "تماس كهربائي",
                        "صعقة", "صعق", "خطر كهربائي", "تسرب غاز", "تسريب غاز", "رائحة غاز",
                        "تسرب مياه قرب الكهرباء", "تسريب مياه قرب الكهرباء", "تسرب مياه بالقرب من الكهرباء",
                        "فيضان", "غرق", "غرقت", "يغمر", "تغمر", "غمر",
                        "لا يوجد كهرباء", "لا توجد كهرباء", "ما فيه كهرباء", "بدون كهرباء",
                        "انقطاع الكهرباء", "انقطاع التيار", "الكهرباء مقطوعة", "انقطعت الكهرباء",
                        "المصعد عالق", "عالقين في المصعد", "علقت في المصعد", "المصعد متوقف بين",
                        "طارئ", "طارئة", "طوارئ",
                       ]

    high_keywords = ["leaking","water leak","leakage","completely stopped",
                     "not working", "broken","dangerous","damage",
                     "very hot","no water",
                     # --- Arabic ---
                    "تسرب", "تسريب", "يسرب", "تسربت",
                    "توقف تماما", "متوقف تماما", "توقفت تماما", "معطل تماما", "متعطل تماما",
                    "لا يعمل", "لا تعمل", "ما يعمل", "ما تعمل", "لا يشتغل", "لا تشتغل",
                    "ما يشتغل", "ما تشتغل", "مو شغال", "خربان", "عطل", "معطل", "متعطل",
                    "مكسور", "انكسر", "مخلوع", "تالف",
                    "خطر", "خطير",
                    "ضرر", "اضرار", "تلف",
                    "حار جدا", "حر شديد", "حر جدا", "ساخن جدا",
                    "لا يوجد ماء", "لا يوجد مياه", "لا توجد مياه", "ما فيه ماء", "ما فيه مياه",
                    "بدون ماء", "بدون مياه", "انقطاع المياه", "انقطاع الماء",
                    "المياه مقطوعة", "الماء مقطوع",
                     ]

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
    if confidence < 50:
        return TicketPriority.MEDIUM

    return TicketPriority.LOW

'''









# Sentiment Analysis
#-------------------------------------------------------

SENTIMENT_AR = {
    "positive": "ايجابي",
    "negative": "سلبي",
    "neutral": "محايد",
}



def localize_sentiment(sentiment: str, language: str) -> str:
    """English sentiment -> the language of the complaint ('ar' or 'en')."""
    return SENTIMENT_AR.get(sentiment, sentiment) if language == "ar" else sentiment

async def _get_sentiment_from_llm(text: str, language: str = "en", max_retries: int = 3) -> str:
    sentiment = await get_sentiment_english(text, max_retries)
    return localize_sentiment(sentiment, language)

async def get_sentiment_from_llm(text: str, max_retries: int = 3) -> str:
    prompt = f"""
            Analyze the sentiment of the following facility management complaint.
            The complaint may be written in Arabic or English.

            Return ONLY one English word, exactly one of:
            positive
            negative
            neutral

            Do not translate the complaint, do not add punctuation or explanations.

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
            if e.response.status_code not in (503, 429):
                return "neutral"

        except Exception as e:
            logger.error(f"Error during Gemini sentiment analysis: {e}")
            return "neutral"

    logger.error("Gemini sentiment analysis failed after all retries — defaulting to neutral")
    return "neutral"







# split complaints
#------------------------------------------------------
SPLIT_EXAMPLES = """
Examples (input -> output):
1. "المكيف خربان والمياه مقطوعة عن الشقة"
   -> {"complaints": ["المكيف خربان", "المياه مقطوعة عن الشقة"]}
2. "المكيف لا يبرد ويطلع صوت مزعج"
   -> {"complaints": ["المكيف لا يبرد ويطلع صوت مزعج"]}   (same air conditioner, one issue)
3. "في تسرب مياه تحت الحوض وكمان اللمبة في الصالة محروقة"
   -> {"complaints": ["في تسرب مياه تحت الحوض", "اللمبة في الصالة محروقة"]}
4. "الكهرباء مقطوعة والمصعد معطل. وكمان الدرج متسخ"
   -> {"complaints": ["الكهرباء مقطوعة", "المصعد معطل", "الدرج متسخ"]}
5. "المكيف خربان وفيه تسرب مياه تحت حوض المطبخ"
   -> {"complaints": ["المكيف خربان", "يوجد تسرب مياه تحت حوض المطبخ"]}
6. "The AC is broken and the kitchen light is not working"
   -> {"complaints": ["The AC is broken", "The kitchen light is not working"]}
"""



# split the complaint text into sentences and return text as list of sentences
async def split_complaints_from_llm(complaint_text: str) -> list[str]:
    # Simple sentence splitting
    prompt = f"""
            You are a professional customer service assistant for a Facility Management company.
            your task is to identify distinct maintainance issues in the 
            customer's message and return each issue as a seperate complaint.
            The message may be in Arabic or English.
             
            Customer Message:
            {json.dumps(complaint_text, ensure_ascii=False)}
             
            Rules:
            1. Return on item for each distinct maintenance issue.
            2. Two issues are DISTINCT when they concern different equipment, systems or places
            (for example: air conditioner vs water leak, electricity vs plumbing, kitchen light vs bathroom tap).
            3. Several symptoms of the SAME equipment or problem are ONE issue
            (for example: "the AC is not cooling and makes noise").
            4. Split distinct issues even when they are joined only by a conjunction such as
            "and", "also", or the Arabic "و" / "وكمان" / "وأيضاً" / "بالإضافة إلى".
            Do NOT split just because a conjunction exists when it is the same issue.
            5. If the message contains only one issue, return one item.
            6. Preserve the original meaning and important details. Do not invent issues or add information.
            7. Each complaint must be understandable on its own: if a part is missing its subject
            after splitting (for example it starts with "وفيه" or "and it has"), restore the subject
            or minimal wording, without adding new information.
            8. Preserve the language of the customer's message. Do NOT translate. Arabic stays Arabic.
            9. Return valid JSON only, using exactly this format:
            {{"complaints": ["complaint 1", "complaint 2"]}}
            10. Do not include explanations or Markdown.

            {SPLIT_EXAMPLES}

            JSON response:
"""
            
            
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.1,
            "maxOutputTokens": 1000,
            "responseMimeType": "application/json"
        }
    }

    headers = {
        "Content-Type": "application/json"
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                GOOGLE_API_URL,
                headers=headers,
                params={"key": GOOGLE_API_KEY},
                json=payload
            )

            
            
            if response.status_code != 200:
                print("Gemini status:", response.status_code)
                print("Gemini error:", response.text)
                response.raise_for_status()

            response.raise_for_status()
            data = response.json()

        raw_text = (
            data["candidates"][0]["content"]["parts"][0]["text"]
        ).strip()

        # Remove Markdown fences if Gemini returns them
        raw_text = re.sub(
            r"^```(?:json)?\s*|\s*```$",
            "",
            raw_text,
            flags=re.IGNORECASE
        ).strip()

        parsed = json.loads(raw_text)
        complaints = parsed.get("complaints")

        if not isinstance(complaints, list):
            raise ValueError(
                "Gemini response must contain a complaints list"
            )

        complaints = [
            item.strip()
            for item in complaints
            if isinstance(item, str) and item.strip()
        ]

        if not complaints:
            raise ValueError(
                "Gemini returned an empty complaints list"
            )

        return complaints

    except Exception as e:
        logger.error(
            f"Failed to split customer complaints: {e}"
        )
        raise
