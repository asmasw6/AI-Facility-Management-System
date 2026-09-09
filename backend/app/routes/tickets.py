
from fastapi import APIRouter, HTTPException
from bson import ObjectId
from bson.errors import InvalidId
from datetime import datetime, timezone

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
def list_tickets():

    tickets = list(
        tickets_collection.find().sort("created_at", -1)
    )

    for ticket in tickets:
        ticket["_id"] = str(ticket["_id"])

        if ticket.get("customer_id"):
            ticket["customer_id"] = str(ticket["customer_id"])

        if ticket.get("call_id"):
            ticket["call_id"] = str(ticket["call_id"])

        if ticket.get("apartment_id"):
            ticket["apartment_id"] = str(ticket["apartment_id"])

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
