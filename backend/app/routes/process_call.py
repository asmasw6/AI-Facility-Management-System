
from fastapi import APIRouter, HTTPException, Depends
from bson.errors import InvalidId
from datetime import datetime, timezone
from bson import ObjectId
from app.database import tickets_collection, customers_collection, calls_collection


from app.models.models import (
    ProcessCallRequest,
    TicketResponse,
)

from app.agents.complaint_agent import complaint_agent
from app.routes.complaints import process_complaint
from app.dependencies.auth import get_current_user

router = APIRouter()


@router.post("/", response_model=TicketResponse)
async def process_call(
    request: ProcessCallRequest,
    current_user: dict = Depends(get_current_user)
):

    try:

        # get customer id from JWT
        customer_id = current_user["customer_id"]
        try:
            object_id = ObjectId(customer_id)
        except InvalidId:   
            raise HTTPException(
                status_code=400,
                detail="Invalid customer ID in JWT"
            )
        
        # check if customer exists
        customer = customers_collection.find_one({
            "_id": object_id }
            )
        if not customer:
            raise HTTPException(
                status_code=404,
                detail="Customer not found"
            )
            
        #create call in DB
        call_data = {
            "customer_id": object_id,
            "transcript": request.text,
            "started_at": datetime.now(timezone.utc),
            "ended_at": datetime.now(timezone.utc),
            "duration": None,
            "audio_url": None
        }
        
        call_result = calls_collection.insert_one(call_data)
        call_id = str(call_result.inserted_id)
        
        # process complaint and create ticket
        result = await process_complaint(
            # get customer id from JWT
            customer_id= customer_id,
            call_id=call_id,
            text=request.text,
        )

        #get ticket
        ticket_id = result.get("ticket_id")

        if not ticket_id:
            raise HTTPException(
                status_code=500,
                detail="Agent failed to create ticket"
            )
            
        
        ticket = tickets_collection.find_one({
            "_id": ObjectId(ticket_id)
        })

        if not ticket:
            raise HTTPException(
                status_code=500,
                detail="Created ticket not found"
            )

        #convert ObjectId to string
        ticket["_id"] = str(ticket["_id"])

        for field in ("customer_id", "call_id", "apartment_id"):
            if ticket.get(field):
                ticket[field] = str(ticket[field])


        # Include call information in the response
        ticket["transcript"] = request.text
        
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
        
        