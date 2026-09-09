from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime
from enum import Enum


# =========================================================
# ENUMS
# =========================================================

class TicketStatus(str, Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"


class TicketPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class BuildingName(str, Enum):
    A = "A"
    B = "B"


class ApartmentNum(str, Enum):
    NUM_201 = "201"
    NUM_202 = "202"
    NUM_203 = "203"
    NUM_204 = "204"
    NUM_205 = "205"
    NUM_206 = "206"
    NUM_207 = "207"
    NUM_208 = "208"


# =========================================================
# COMMON CONFIG
# =========================================================

class MongoBaseModel(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True
    )


# =========================================================
# BUILDING
# =========================================================

class BuildingCreate(MongoBaseModel):
    building_name: BuildingName


class BuildingResponse(MongoBaseModel):
    id: str = Field(alias="_id")
    building_name: BuildingName


# =========================================================
# APARTMENT
# =========================================================

class ApartmentCreate(MongoBaseModel):
    apartment_number: ApartmentNum
    building_id: str


class ApartmentResponse(MongoBaseModel):
    id: str = Field(alias="_id")
    apartment_number: ApartmentNum
    building_id: str


# =========================================================
# CUSTOMER
# =========================================================

class CustomerCreate(MongoBaseModel):
    name: str
    phone: Optional[str] = None
    email: Optional[str] = None
    apartment_id: str


class CustomerResponse(MongoBaseModel):
    id: str = Field(alias="_id")
    name: str
    phone: Optional[str] = None
    email: Optional[str] = None
    apartment_id: str
    created_at: datetime


# =========================================================
# CALL
# =========================================================

class CallCreate(MongoBaseModel):
    customer_id: str
    transcript: Optional[str] = None
    audio_url: Optional[str] = None


class CallEnd(MongoBaseModel):
    transcript: Optional[str] = None
    audio_url: Optional[str] = None


class CallResponse(MongoBaseModel):
    id: str = Field(alias="_id")
    customer_id: str
    transcript: Optional[str] = None
    started_at: datetime
    ended_at: Optional[datetime] = None
    duration: Optional[int] = None
    audio_url: Optional[str] = None


# =========================================================
# TICKET
# =========================================================

class ProcessCallRequest(MongoBaseModel):
    customer_id: str
    call_id: Optional[str] = None

    text: str = Field(
        ...,
        description="Text extracted from the customer's call transcript, which describes the issue they are facing.>>>"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "customer_id": "68b123456789abcdef123456",
                "call_id": "68b987654321abcdef123456",
                "text": "The air conditioner is leaking water and is no longer cooling the apartment."
            }
        }
    )


class TicketResponse(MongoBaseModel):
    id: str = Field(alias="_id")
    customer_id: str
    call_id: Optional[str] = None
    apartment_id: str

    issue_description: str
    predicted_category: str
    confidence: Optional[float] = None
    sentiment: Optional[str] = None

    priority: TicketPriority
    priority_reason: Optional[str] = None

    route: Optional[str] = None
    routing_team: Optional[str] = None

    status: TicketStatus

    ai_response: Optional[str] = None

    created_at: datetime
    resolved_at: Optional[datetime] = None


class TicketUpdate(MongoBaseModel):
    status: Optional[TicketStatus] = None
    priority: Optional[TicketPriority] = None