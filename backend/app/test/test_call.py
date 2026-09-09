from main import determine_priority
import asyncio
from bert_classifier import ComplaintClassifier
from llm_service import generate_llm_response, get_sentiment_from_llm

classifier = ComplaintClassifier("model")


async def test_call():
    print("\n" + "=" * 50)
    print("      AI FACILITY MANAGEMENT SYSTEM")
    print("=" * 50)

    print("\nType 'exit' to stop.\n")

    while True:
        complaint = input("Enter Your Complaint: ").strip()

        if complaint.lower() == "exit":
            print("\nSystem closed.")
            break

        if not complaint:
            continue

        print("\nProcessing...\n")

        try:
            # Category prediction
            category, confidence = classifier.predict(complaint)

            # Sentiment analysis
            sentiment = await get_sentiment_from_llm(complaint)

            # Priority
            priority = determine_priority(
                category=category,
                sentiment=sentiment,
                confidence=confidence,
                complaint_text=complaint
            )

            # AI response
            ai_response = await generate_llm_response(
                complaint_text=complaint,
                category=category,
                sentiment=sentiment,
                priority=priority,
                building_number="n/a",
                apartment_number="n/a"
            )

            print("-" * 50)
            print(f"Complaint   : {complaint}")
            print(f"Category   : {category}")
            print(f"Confidence : {confidence:.2f}")
            print(f"Sentiment  : {sentiment}")
            print(f"Priority   : {priority.value}")
            print(f"Status     : Open")

            print("\nAI Response:")
            print(ai_response)

            print("-" * 50)

        except Exception as e:
            import traceback
            traceback.print_exc()



if __name__ == "__main__":
    import asyncio
    asyncio.run(test_call())