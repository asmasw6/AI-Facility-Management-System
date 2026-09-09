

'''

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
                
                
            # -----------------------------------------
            # Debug information
            # -----------------------------------------

            logger.info(
                f"Gemini sentiment status: "
                f"{response.status_code}"
            )

            # -----------------------------------------
            # Retry temporary errors
            # -----------------------------------------
 
                
                
                
                

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

'''


'''
async def get_sentiment_from_llm(text: str, max_retries: int = 2) -> str:
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
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0,
            "maxOutputTokens": 100
        }
    }

    headers = {
        "Content-Type": "application/json"
    }

    valid_sentiments = {"positive", "negative", "neutral"}

    for attempt in range(max_retries):
        try:
            logger.info(
                f"Sending sentiment request to Gemini... "
                f"attempt {attempt + 1}/{max_retries}"
            )

            async with httpx.AsyncClient(
                timeout=httpx.Timeout(
                    connect=10.0,
                    read=15.0,
                    write=10.0,
                    pool=10.0
                )
            ) as client:

                response = await client.post(
                    GOOGLE_API_URL,
                    headers=headers,
                    params={"key": GOOGLE_API_KEY},
                    json=payload
                )

            logger.info(
                f"Gemini sentiment status: {response.status_code}"
            )

            if response.status_code in (429, 503):
                wait_time = 2 ** attempt

                logger.warning(
                    f"Gemini unavailable ({response.status_code}). "
                    f"Retrying in {wait_time}s..."
                )

                await asyncio.sleep(wait_time)
                continue

            response.raise_for_status()

            data = response.json()

            candidates = data.get("candidates", [])

            if not candidates:
                logger.warning(
                    "Gemini returned no candidates"
                )
                return "neutral"

            content = candidates[0].get("content", {})

            parts = content.get("parts", [])

            if not parts:
                logger.warning(
                    f"Gemini returned no parts. Response: {data}"
                )
                return "neutral"

            sentiment_raw = (
                parts[0]
                .get("text", "")
                .strip()
                .lower()
            )

            # Clean possible extra text
            sentiment_raw = sentiment_raw.split()[0] if sentiment_raw else ""

            if sentiment_raw not in valid_sentiments:
                logger.warning(
                    f"Unexpected sentiment: {sentiment_raw!r}"
                )
                return "neutral"

            logger.info(
                f"Sentiment detected: {sentiment_raw}"
            )

            return sentiment_raw

        except httpx.TimeoutException:
            logger.warning(
                "Gemini sentiment request timed out"
            )

            if attempt < max_retries - 1:
                await asyncio.sleep(1)
                continue

            return "neutral"

        except httpx.HTTPStatusError as e:
            logger.error(
                f"Gemini sentiment HTTP error: "
                f"{e.response.status_code} - "
                f"{e.response.text}"
            )

            return "neutral"

        except Exception as e:
            logger.exception(
                f"Unexpected sentiment error: {e}"
            )
            return "neutral"

    return "neutral"


'''