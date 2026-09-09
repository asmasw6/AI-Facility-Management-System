

from fastapi import APIRouter, HTTPException
from bson import ObjectId
from bson.errors import InvalidId
from datetime import datetime, timezone

from app.database import calls_collection, customers_collection
from app.models.models import CallCreate, CallEnd, CallResponse

router = APIRouter()


# Create Call
@router.post("/", response_model=CallResponse)
def create_call(call: CallCreate):

    # Validate customer_id
    try:
        customer_id = ObjectId(call.customer_id)
    except InvalidId:
        raise HTTPException(
            status_code=400,
            detail="Invalid customer ID"
        )

    # Check customer exists
    customer = customers_collection.find_one({
        "_id": customer_id
    })

    if not customer:
        raise HTTPException(
            status_code=404,
            detail="Customer not found"
        )

    # Create call
    call_data = {
        "customer_id": customer_id,
        "transcript": call.transcript,
        "started_at": datetime.now(timezone.utc),
        "ended_at": None,
        "duration": None,
        "audio_url": call.audio_url
    }

    result = calls_collection.insert_one(call_data)

    created_call = calls_collection.find_one({
        "_id": result.inserted_id
    })

    # Convert ObjectId to string
    created_call["_id"] = str(created_call["_id"])
    created_call["customer_id"] = str(
        created_call["customer_id"]
    )

    return created_call


# Get All Calls
@router.get("/", response_model=list[CallResponse])
def get_calls():

    calls = list(
        calls_collection.find()
    )

    for call in calls:
        call["_id"] = str(call["_id"])
        call["customer_id"] = str(
            call["customer_id"]
        )

    return calls


# Get Call by ID
@router.get("/{call_id}", response_model=CallResponse)
def get_call(call_id: str):

    try:
        object_id = ObjectId(call_id)
    except InvalidId:
        raise HTTPException(
            status_code=400,
            detail="Invalid call ID"
        )

    call = calls_collection.find_one({
        "_id": object_id
    })

    if not call:
        raise HTTPException(
            status_code=404,
            detail="Call not found"
        )

    call["_id"] = str(call["_id"])
    call["customer_id"] = str(
        call["customer_id"]
    )

    return call


# Get Calls by Customer
@router.get(
    "/customer/{customer_id}",
    response_model=list[CallResponse]
)
def get_calls_by_customer(customer_id: str):

    try:
        object_id = ObjectId(customer_id)
    except InvalidId:
        raise HTTPException(
            status_code=400,
            detail="Invalid customer ID"
        )

    calls = list(
        calls_collection.find({
            "customer_id": object_id
        })
    )

    for call in calls:
        call["_id"] = str(call["_id"])
        call["customer_id"] = str(
            call["customer_id"]
        )

    return calls


# End Call
@router.put("/{call_id}/end", response_model=CallResponse)
def end_call(call_id: str, call_end: CallEnd):

    try:
        object_id = ObjectId(call_id)
    except InvalidId:
        raise HTTPException(
            status_code=400,
            detail="Invalid call ID"
        )

    # Get existing call
    existing_call = calls_collection.find_one({
        "_id": object_id
    })

    if not existing_call:
        raise HTTPException(
            status_code=404,
            detail="Call not found"
        )

    # End time
    ended_at = datetime.now(timezone.utc)

    # Calculate duration
    started_at = existing_call["started_at"]

    duration = int(
        (ended_at - started_at).total_seconds()
    )

    update_data = {
        "ended_at": ended_at,
        "duration": duration
    }

    # Update transcript if provided
    if call_end.transcript is not None:
        update_data["transcript"] = call_end.transcript

    # Update audio URL if provided
    if call_end.audio_url is not None:
        update_data["audio_url"] = call_end.audio_url

    calls_collection.update_one(
        {"_id": object_id},
        {"$set": update_data}
    )

    updated_call = calls_collection.find_one({
        "_id": object_id
    })

    updated_call["_id"] = str(
        updated_call["_id"]
    )

    updated_call["customer_id"] = str(
        updated_call["customer_id"]
    )

    return updated_call
