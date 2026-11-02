
from fastapi import APIRouter, HTTPException, Depends
from bson import ObjectId
from bson.errors import InvalidId
from datetime import datetime, timezone,  time, timedelta
from app.dependencies.auth import get_current_user
from app.database import tickets_collection
from app.models.models import (
    TicketResponse,
    TicketUpdate,
    TicketStatus
)

router = APIRouter()


# ===========================================================
# GET ALL TICKETS
# ===========================================================

@router.get("/", response_model=list[TicketResponse])
def list_tickets( current_user=Depends(get_current_user)):


    customer_id = current_user.get("customer_id")
    
    if not customer_id:
        raise HTTPException(
            status_code=400,
            detail="Customer ID not found"
        )
        
    tickets = list(
        tickets_collection.find({
            "customer_id": ObjectId(customer_id)
        }).sort("created_at", -1)
    )
    
    
    for ticket in tickets:
        ticket["_id"] = str(ticket["_id"])

        for field in ['customer_id', 'call_id', 'apartment_id']:
            if ticket.get(field):
                ticket[field] = str(ticket[field])

    return tickets


# ===========================================================
# GET TICKET BY ID
# ===========================================================

@router.get("/{ticket_id}", response_model=TicketResponse)
def get_ticket(ticket_id: str):

    try:
        object_id = ObjectId(ticket_id)
    except InvalidId:
        raise HTTPException(
            status_code=400,
            detail="Invalid ticket ID"
        )

    ticket = tickets_collection.find_one({
        "_id": object_id
    })

    if not ticket:
        raise HTTPException(
            status_code=404,
            detail="Ticket not found"
        )

    ticket["_id"] = str(ticket["_id"])

    if ticket.get("customer_id"):
        ticket["customer_id"] = str(ticket["customer_id"])

    if ticket.get("call_id"):
        ticket["call_id"] = str(ticket["call_id"])

    if ticket.get("apartment_id"):
        ticket["apartment_id"] = str(ticket["apartment_id"])

    return ticket


# ===========================================================
# UPDATE TICKET
# ===========================================================

@router.patch("/{ticket_id}", response_model=TicketResponse)
def update_ticket(
    ticket_id: str,
    payload: TicketUpdate
):

    try:
        object_id = ObjectId(ticket_id)
    except InvalidId:
        raise HTTPException(
            status_code=400,
            detail="Invalid ticket ID"
        )

    ticket = tickets_collection.find_one({
        "_id": object_id
    })

    if not ticket:
        raise HTTPException(
            status_code=404,
            detail="Ticket not found"
        )

    update_data = {}

    if payload.status is not None:

        update_data["status"] = payload.status.value

        if payload.status == TicketStatus.RESOLVED:
            update_data["resolved_at"] = datetime.now(timezone.utc)

    if payload.priority is not None:
        update_data["priority"] = payload.priority.value

    if update_data:

        tickets_collection.update_one(
            {"_id": object_id},
            {"$set": update_data}
        )

    updated_ticket = tickets_collection.find_one({
        "_id": object_id
    })

    updated_ticket["_id"] = str(updated_ticket["_id"])

    if updated_ticket.get("customer_id"):
        updated_ticket["customer_id"] = str(
            updated_ticket["customer_id"]
        )

    if updated_ticket.get("call_id"):
        updated_ticket["call_id"] = str(
            updated_ticket["call_id"]
        )

    if updated_ticket.get("apartment_id"):
        updated_ticket["apartment_id"] = str(
            updated_ticket["apartment_id"]
        )

    return updated_ticket



@router.delete("/tickets/{ticket_id}")
async def delete_ticket(
    ticket_id: str,
    current_user: dict = Depends(get_current_user)
):
    try:
        ticket_object_id = ObjectId(ticket_id)
    except InvalidId:
        raise HTTPException(
            status_code=400,
            detail="Invalid ticket ID"
        )

    result = await db.tickets.delete_one({
        "_id": ticket_object_id
    })

    if result.deleted_count == 0:
        raise HTTPException(
            status_code=404,
            detail="Ticket not found"
        )

    return {"message": "Ticket deleted successfully"}

'''
@router.delete("/today")
async def delete_today_tickets(
    current_user: dict = Depends(get_current_user)
):
    customer_id = ObjectId(current_user["customer_id"])

    # Saudi Arabia timezone (UTC+3)
    saudi_tz = timezone(timedelta(hours=3))
    now = datetime.now(saudi_tz)

    # Start and end of today in Saudi time
    start_of_day = datetime.combine(
        now.date(), time.min, tzinfo=saudi_tz
    )
    start_of_next_day = start_of_day + timedelta(days=1)

    # Convert Saudi time to UTC
    start_utc = start_of_day.astimezone(timezone.utc)
    end_utc = start_of_next_day.astimezone(timezone.utc)

    # Delete today's tickets for the logged-in customer
    result = tickets_collection.delete_many({
        "customer_id": customer_id,
        "created_at": {
            "$gte": start_utc,
            "$lt": end_utc
        }
    })

    return {
        "message": "Today's tickets deleted successfully",
        "deleted_count": result.deleted_count
    }
    
    '''