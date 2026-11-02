from pydantic import BaseModel, Field, ConfigDict, EmailStr
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


class RegistrationStatus(str, Enum):
    AVAILABLE = "available"
    REGISTERED = "registered"


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
    id: str = Field(alias="_id")# 7878 , 7854
    apartment_number: ApartmentNum #201, 201
    building_id: str # A, B
    apartment_code: str  # A-201, B-202, from the building name and apartment number
    registration_code: str  # Unique code for registration
    registration_status: RegistrationStatus


# =========================================================
# CUSTOMER
# =========================================================
'''
class CustomerCreate(MongoBaseModel):
    name: str
    phone: Optional[str] = None
    email: Optional[str] = None
    apartment_id: str # id= 7854 , ap-num= 201, Building= B  
'''
"""
Name
Phone
Email
Password
Apartment Code: A-201
Registration Code: 839274 by the building management

""" 

class CustomerResponse(MongoBaseModel):
    id: str = Field(alias="_id")
    name: str
    phone: Optional[str] = None
    email: Optional[str] = None
    apartment_id: str
    created_at: datetime

class CustomerRegister(MongoBaseModel):
    name: str
    phone: str
    email: EmailStr
    password: str
    apartment_code: str  # id= 7854 , ap-num= 201, Building= B
    registration_code: str  # Unique code for registration
    
# Login
class CustomerLogin(MongoBaseModel):
    email: EmailStr
    password: str
    
class LoginResponse(MongoBaseModel):
    access_token: str
    token_type: str
    customer: CustomerResponse
   
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
    
#=========================================================
# Voice Response
#=========================================================
'''
class VoiceResponse(MongoBaseModel):
    id: str = Field(alias="_id")
    customer_id: str
    transcript: str
    audio_url: str

    
 
    call_id: str

    category: Optional[str] = None
    confidence: Optional[float] = None
    sentiment: Optional[str] = None
    priority: Optional[str] = None
    routing_team: Optional[str] = None

    ai_response: Optional[str] = None
    ticket_id: Optional[str] = None
'''
  
#=========================================================
# TTS
#=========================================================  
class TTSRequest(BaseModel):
    text: str
    
      
#=========================================================
# Complaints
# =========================================================


class ComplaintRequest(BaseModel):
    customer_id: str
    call_id: Optional[str] = None
    text: str

# =========================================================
# TICKET
# =========================================================

class ProcessCallRequest(MongoBaseModel):
    text: str = Field(
        ...,
        description="Text extracted from the customer's call transcript, which describes the issue they are facing.>>>"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
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