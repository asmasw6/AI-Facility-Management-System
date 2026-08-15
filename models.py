

from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Enum, ForeignKey
)

from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from pydantic import BaseModel, Field
from typing import  Optional
from datetime import datetime
import enum

from database import Base


class TicketStatus(str, enum.Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"   

class TicketPriority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"
    
class Customer(Base):
    __tablename__ = "Customers"
    
    customer_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)    
    phone = Column(String(30), nullable=True, index=True)    
    email = Column(String(150), nullable=True)    
    created_at = Column(DateTime(timezone=True), server_default=func.now()) 
    
    calls = relationship("Call", back_populates="customer")
    tickets = relationship("Ticket", back_populates="customer", cascade="all, delete-orphan")
    
    
    
class Call(Base):
    __tablename__ = "Calls"
    
    call_id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("Customers.customer_id"), nullable=False, index=True   )
    
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    ended_at = Column(DateTime(timezone=True), nullable=True)
    transcript = Column(Text, nullable=True)
    duration = Column(Integer, nullable=True)
    audio_url = Column(String(500), nullable=True)

    customer = relationship("Customer", back_populates="calls")
    tickets = relationship("Ticket", back_populates="call", cascade="all, delete-orphan")

class Ticket(Base):
    __tablename__ = "Tickets" 
    
    ticket_id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("Customers.customer_id"), nullable=False, index=True)
    call_id = Column(Integer, ForeignKey("Calls.call_id"), nullable=True, index=True)

    issue_description = Column(Text, nullable=False)
    predicted_category = Column(String(100), nullable=False, index=True)
    priority = Column(Enum(TicketPriority), default=TicketPriority.MEDIUM, nullable=False)
    status = Column(Enum(TicketStatus), default=TicketStatus.OPEN, nullable=False)
    ai_response = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    resolved_at = Column(DateTime(timezone=True), nullable=True)

    customer = relationship("Customer", back_populates="tickets")
    call = relationship("Call", back_populates="tickets")
    
# Pydantic Schemas - CUSTOMER
   
    
class CustomerCreate(BaseModel):
    name: str
    phone: Optional[str] = None
    email: Optional[str] = None


class CustomerResponse(BaseModel):
    customer_id: int
    name: str
    phone: Optional[str]
    email: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True
 
 
 
# Pydantic Schemas - CALL
      
class CallCreate(BaseModel):
    customer_id: int
    transcript: Optional[str] = None
    audio_url: Optional[str] = None


class CallEnd(BaseModel):
    transcript: Optional[str] = None
    audio_url: Optional[str] = None


class CallResponse(BaseModel):
    call_id: int
    customer_id: int
    transcript: Optional[str]
    started_at: datetime
    ended_at: Optional[datetime]
    duration: Optional[int]
    audio_url: Optional[str]

    class Config:
        from_attributes = True



# Pydantic Schemas - TICKET
#-----------------------------------------


class ProcessCallRequest(BaseModel):
    customer_id: int
    call_id : Optional[int] = None
    text: str = Field(..., description="نص الشكوى/المكالمة القادم من STT")    
    
    
    class Config:
        json_schema_extra = {
            "example": {
                "customer_id": 1,
                "call_id": 1,
                "text": "The air conditioner is leaking water and is no longer cooling the apartment."
            }
        }
        
        
# -----> Customer → Call starts → STT converts speech to text → ProcessCallRequest → BERT analyzes complaint → Ticket created



class TicketResponse(BaseModel):
    ticket_id: int
    customer_id: int
    call_id: Optional[int]
    issue_description: str
    predicted_category: str
    priority: TicketPriority
    status: TicketStatus
    ai_response: Optional[str]
    created_at: datetime
    resolved_at: Optional[datetime]

    class Config:
        from_attributes = True
        

class TicketUpdate(BaseModel):
    status: Optional[TicketStatus] = None
    priority: Optional[TicketPriority] = None


