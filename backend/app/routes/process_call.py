
from fastapi import APIRouter, HTTPException
from bson.errors import InvalidId
from bson import ObjectId

from app.models.models import (
    ProcessCallRequest,
    TicketResponse,
)

from app.agents.complaint_agent import complaint_agent


router = APIRouter()


@router.post("/", response_model=TicketResponse)
async def process_call(request: ProcessCallRequest):

    try:

        result = await complaint_agent.ainvoke({
            "customer_id": request.customer_id,
            "call_id": request.call_id,
            "text": request.text,
        })

        ticket_id = result.get("ticket_id")

        if not ticket_id:
            raise HTTPException(
                status_code=500,
                detail="Agent failed to create ticket"
            )

        from app.database import tickets_collection

        ticket = tickets_collection.find_one({
            "_id": ObjectId(ticket_id)
        })

        if not ticket:
            raise HTTPException(
                status_code=500,
                detail="Created ticket not found"
            )

        ticket["_id"] = str(ticket["_id"])

        if ticket.get("customer_id"):
            ticket["customer_id"] = str(
                ticket["customer_id"]
            )

        if ticket.get("call_id"):
            ticket["call_id"] = str(
                ticket["call_id"]
            )

        if ticket.get("apartment_id"):
            ticket["apartment_id"] = str(
                ticket["apartment_id"]
            )

        return ticket

    except InvalidId:
        raise HTTPException(
            status_code=400,
            detail="Invalid ID"
        )

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Agent processing error: {str(e)}"
        )














'''
from fastapi import APIRouter, HTTPException
from bson import ObjectId
from bson.errors import InvalidId
from datetime import datetime, timezone
import logging

from app.database import (
    customers_collection,
    calls_collection,
    apartments_collection,
    buildings_collection,
    tickets_collection,
)

from app.models.models import (
    ProcessCallRequest,
    TicketResponse,
    TicketStatus,
)

from app.routes.ai import classifier

from app.services.llm_service import (
    get_sentiment_from_llm,
    determine_priority,
    generate_llm_response,
)


router = APIRouter()

logger = logging.getLogger(__name__)


@router.post("/", response_model=TicketResponse)
async def process_call(request: ProcessCallRequest):

    # =========================================================
    # 1. Check BERT classifier
    # =========================================================

    if classifier is None:
        raise HTTPException(
            status_code=503,
            detail="BERT classifier is not loaded yet"
        )

    # =========================================================
    # 2. Validate customer ID
    # =========================================================

    try:
        customer_id = ObjectId(request.customer_id)

    except InvalidId:
        raise HTTPException(
            status_code=400,
            detail="Invalid customer ID"
        )

    # =========================================================
    # 3. Find customer
    # =========================================================

    customer = customers_collection.find_one({
        "_id": customer_id
    })

    if not customer:
        raise HTTPException(
            status_code=404,
            detail="Customer not found"
        )

    # =========================================================
    # 4. Validate call if provided
    # =========================================================

    call_id = None

    if request.call_id is not None:

        try:
            call_id = ObjectId(request.call_id)

        except InvalidId:
            raise HTTPException(
                status_code=400,
                detail="Invalid call ID"
            )

        call = calls_collection.find_one({
            "_id": call_id
        })

        if not call:
            raise HTTPException(
                status_code=404,
                detail="Call not found"
            )

        # Make sure this call belongs to this customer
        if call.get("customer_id") != customer_id:
            raise HTTPException(
                status_code=400,
                detail="Call does not belong to this customer"
            )

    # =========================================================
    # 5. Get customer's apartment
    # =========================================================

    apartment_id = customer.get("apartment_id")

    if not apartment_id:
        raise HTTPException(
            status_code=400,
            detail="Customer is not assigned to an apartment"
        )

    apartment = apartments_collection.find_one({
        "_id": apartment_id
    })

    if not apartment:
        raise HTTPException(
            status_code=404,
            detail="Apartment not found"
        )

    # =========================================================
    # 6. Get building
    # =========================================================

    building_id = apartment.get("building_id")

    if not building_id:
        raise HTTPException(
            status_code=400,
            detail="Apartment is not assigned to a building"
        )

    building = buildings_collection.find_one({
        "_id": building_id
    })

    if not building:
        raise HTTPException(
            status_code=404,
            detail="Building not found"
        )

    building_number = building["building_name"]
    apartment_number = apartment["apartment_number"]

    # =========================================================
    # 7. BERT classification
    # =========================================================

    try:

        category, confidence = classifier.predict(
            request.text
        )

        logger.info(
            f"BERT prediction: "
            f"category={category}, "
            f"confidence={confidence:.4f}"
        )

    except Exception as e:

        logger.error(
            f"Error during BERT prediction: {e}"
        )

        raise HTTPException(
            status_code=500,
            detail="Error during BERT prediction"
        )

    # =========================================================
    # 8. Sentiment analysis using LLM
    # =========================================================

    sentiment = await get_sentiment_from_llm(
        request.text
    )

    logger.info(
        f"LLM sentiment: {sentiment}"
    )

    # =========================================================
    # 9. Determine priority
    # =========================================================

    priority = determine_priority(
        category=category,
        sentiment=sentiment,
        confidence=confidence,
        complaint_text=request.text
    )

    logger.info(
        f"Ticket priority: {priority.value}"
    )

    # =========================================================
    # 10. Generate AI response
    # =========================================================

    ai_response = await generate_llm_response(
        complaint_text=request.text,
        category=category,
        sentiment=sentiment,
        priority=priority.value,
        building_number=building_number,
        apartment_number=apartment_number,
    )

    # =========================================================
    # 11. Create ticket in MongoDB
    # =========================================================

    ticket_data = {
        "customer_id": customer_id,
        "call_id": call_id,
        "apartment_id": apartment_id,
        "issue_description": request.text,
        "predicted_category": category,
        "priority": priority.value,
        "status": TicketStatus.OPEN.value,
        "ai_response": ai_response,
        "created_at": datetime.now(timezone.utc),
        "resolved_at": None,
    }

    result = tickets_collection.insert_one(
        ticket_data
    )

    # =========================================================
    # 12. Get created ticket
    # =========================================================

    created_ticket = tickets_collection.find_one({
        "_id": result.inserted_id
    })

    if not created_ticket:
        raise HTTPException(
            status_code=500,
            detail="Failed to create ticket"
        )

    # =========================================================
    # 13. Convert ObjectIds to strings
    # =========================================================

    created_ticket["_id"] = str(
        created_ticket["_id"]
    )

    created_ticket["customer_id"] = str(
        created_ticket["customer_id"]
    )

    if created_ticket.get("call_id"):
        created_ticket["call_id"] = str(
            created_ticket["call_id"]
        )

    created_ticket["apartment_id"] = str(
        created_ticket["apartment_id"]
    )

    # =========================================================
    # 14. Logging
    # =========================================================

    logger.info(
        f"Ticket created successfully | "
        f"Ticket={created_ticket['_id']} | "
        f"Building={building_number} | "
        f"Apartment={apartment_number} | "
        f"Category={category} | "
        f"Priority={priority.value}"
    )

    return created_ticket
'''