from typing import TypedDict, Optional

from app.routes.ai import classifier
from app.services.llm_service import (
    get_sentiment_from_llm,
    determine_priority,
    generate_llm_response,
)

from app.database import (
    customers_collection,
    calls_collection,
    apartments_collection,
    buildings_collection,
    tickets_collection,
)

from app.models.models import TicketStatus, TicketPriority

from bson import ObjectId
from datetime import datetime, timezone
from langgraph.graph import StateGraph, END

# Agent State
#----------------------------------------------
class ComplaintState(TypedDict, total=False):
    # Input
    customer_id: str
    call_id: Optional[str]
    text: str

    # Database information
    apartment_id: ObjectId
    building_number: str
    apartment_number: str

    # AI results
    category: str
    confidence: float
    sentiment: str
    priority: str
    route: str
    routing_team: str
    priority_reason: str
    ai_response: str
    


    # Result
    ticket_id: str
    
# 1. Node: Check from the Customer, retrieve the apartment and building information from the database.
#-------------------------------------------------------------
def load_customer_data(state: ComplaintState):
    customer_id = ObjectId(state["customer_id"])

    customer = customers_collection.find_one({
        "_id": customer_id
    })

    if not customer:
        raise ValueError("Customer not found")

    apartment_id = customer.get("apartment_id")

    if not apartment_id:
        raise ValueError("Customer is not assigned to an apartment")

    apartment = apartments_collection.find_one({
        "_id": apartment_id
    })

    if not apartment:
        raise ValueError("Apartment not found")

    building_id = apartment.get("building_id")

    if not building_id:
        raise ValueError("Apartment is not assigned to a building")

    building = buildings_collection.find_one({
        "_id": building_id
    })

    if not building:
        raise ValueError("Building not found")

    return {
        "apartment_id": apartment_id,
        "building_number": building["building_name"],
        "apartment_number": apartment["apartment_number"],
    }
    
    
# 2. Node: Check from call
#-------------------------------------------------------------
def validate_call(state: ComplaintState):
    call_id = state.get("call_id")

    if not call_id:
        return {}

    call_object_id = ObjectId(call_id)
    customer_object_id = ObjectId(state["customer_id"])

    call = calls_collection.find_one({
        "_id": call_object_id
    })

    if not call:
        raise ValueError("Call not found")

    if call.get("customer_id") != customer_object_id:
        raise ValueError("Call does not belong to this customer")

    return {}


# 3. Node: Classification of  the complaint text using Bert model
#-------------------------------------------------------------
def classify_complaint(state: ComplaintState):
    if classifier is None:
        raise ValueError("BERT classifier is not loaded")

    category, confidence = classifier.predict(
        state["text"]
    )

    return {
        "category": category,
        "confidence": confidence,
    }
    
# 4. Node: Sentiment analysis of the complaint text using LLM
#-------------------------------------------------------------
'''
async def analyze_sentiment(state: ComplaintState):
    sentiment = await get_sentiment_from_llm(
        state["text"]
    )

    return {
        "sentiment": sentiment
    }
    
'''

async def analyze_sentiment(state: ComplaintState):
    try:
        sentiment = await get_sentiment_from_llm(state["text"])

        if sentiment not in {"positive", "negative", "neutral"}:
            sentiment = "neutral"

        return {
            "sentiment": sentiment
        }

    except Exception as e:
        print(f"Sentiment node failed: {e}")

        return {
            "sentiment": "neutral"
        }
    
# 5. Node: Determine the priority of the complaint
#-------------------------------------------------------------
def determine_ticket_priority(state: ComplaintState):

    priority = determine_priority(
        category=state["category"],
        sentiment=state["sentiment"],
        confidence=state["confidence"],
        complaint_text=state["text"],
    )

    # Explain WHY the priority was selected
    if priority == TicketPriority.URGENT:

        reason = (
            "The complaint contains a potential safety "
            "or emergency-related issue that requires "
            "immediate attention."
        )

    elif priority == TicketPriority.HIGH:

        reason = (
            "The complaint indicates a significant "
            "maintenance issue that should be handled "
            "with high priority."
        )

    elif priority == TicketPriority.MEDIUM:

        reason = (
            "The complaint requires attention but does "
            "not indicate an immediate emergency."
        )

    else:

        reason = (
            "The complaint does not indicate an urgent "
            "or high-impact maintenance issue."
        )

    return {
        "priority": priority.value,
        "priority_reason": reason,
    }



# 5.1. AGENT DECISION — Conditional Routing
#-------------------------------------------------------------
def route_by_priority(state: ComplaintState):

    priority = state["priority"]

    if priority == TicketPriority.URGENT.value:
        return "emergency"

    if priority == TicketPriority.HIGH.value:
        return "fast_track"

    return "standard"


# 5.2. Emergency Path
#-------------------------------------------------------------
def emergency_path(state: ComplaintState):

    return {
        "route": "emergency",
        "routing_team": "Emergency Maintenance Team",
    }


# 5.3 Fast Track Path
#-------------------------------------------------------------
def fast_track_path(state: ComplaintState):

    team_by_category = {
        "Electricity Issue": "Electrical Maintenance Team",
        "Security Complaint": "Security Team",
        "Plumbing Issue": "Plumbing Maintenance Team",
        "Water Supply Request": "Water Supply Team",
    }

    team = team_by_category.get(
        state["category"],
        "Priority Maintenance Team"
    )

    return {
        "route": "fast_track",
        "routing_team": team,
    }


# 5.4. Standard Path
#-------------------------------------------------------------
def standard_path(state: ComplaintState):

    team_by_category = {
        "Electricity Issue": "Electrical Maintenance Team",
        "Security Complaint": "Security Team",
        "Plumbing Issue": "Plumbing Maintenance Team",
        "Water Supply Request": "Water Supply Team",
    }

    team = team_by_category.get(
        state["category"],
        "General Maintenance Team"
    )

    return {
        "route": "standard",
        "routing_team": team,
    }

    
# 6. Node: LLMs Response
#-------------------------------------------------------------
async def generate_customer_response(state: ComplaintState):
    response = await generate_llm_response(
        complaint_text=state["text"],
        category=state["category"],
        sentiment=state["sentiment"],
        priority=state["priority"],
        building_number=state["building_number"],
        apartment_number=state["apartment_number"],
    )

    return {
        "ai_response": response
    }
    
    
# 7. Node: Create a ticket in the database
#------------------------------------------------------------- 
def create_ticket(state: ComplaintState):
    customer_id = ObjectId(state["customer_id"])

    call_id = None

    if state.get("call_id"):
        call_id = ObjectId(state["call_id"])

    ticket_data = {
    "customer_id": customer_id,
    "call_id": call_id,
    "apartment_id": state["apartment_id"],

    "issue_description": state["text"],
    "predicted_category": state["category"],
    "confidence": state["confidence"],
    "sentiment": state["sentiment"],

    "priority": state["priority"],
    "priority_reason": state["priority_reason"],

    "route": state["route"],
    "routing_team": state["routing_team"],

    "status": TicketStatus.OPEN.value,
    "ai_response": state["ai_response"],

    "created_at": datetime.now(timezone.utc),
    "resolved_at": None,
}

    result = tickets_collection.insert_one(ticket_data)

    return {
        "ticket_id": str(result.inserted_id)
    }
    
 
 
# 8. Build LangGraph StateGraph
#-------------------------------------------------------------  
def build_complaint_agent():

    graph = StateGraph(ComplaintState)

    graph.add_node(
        "load_customer_data",
        load_customer_data
    )

    graph.add_node(
        "validate_call",
        validate_call
    )

    graph.add_node(
        "classify_complaint",
        classify_complaint
    )

    graph.add_node(
        "analyze_sentiment",
        analyze_sentiment
    )

    graph.add_node(
        "determine_priority",
        determine_ticket_priority
    )

    # Agent Decision Paths
    graph.add_node(
        "emergency_path",
        emergency_path
    )

    graph.add_node(
        "fast_track_path",
        fast_track_path
    )

    graph.add_node(
        "standard_path",
        standard_path
    )

    graph.add_node(
        "generate_response",
        generate_customer_response
    )

    graph.add_node(
        "create_ticket",
        create_ticket
    )

    graph.set_entry_point("load_customer_data")

    graph.add_edge(
        "load_customer_data",
        "validate_call"
    )

    graph.add_edge(
        "validate_call",
        "classify_complaint"
    )

    graph.add_edge(
        "classify_complaint",
        "analyze_sentiment"
    )

    graph.add_edge(
        "analyze_sentiment",
        "determine_priority"
    )

    # Agent Decision
    graph.add_conditional_edges(
        "determine_priority",
        route_by_priority,
        {
            "emergency": "emergency_path",
            "fast_track": "fast_track_path",
            "standard": "standard_path",
        }
    )

    # All paths continue to response generation
    graph.add_edge(
        "emergency_path",
        "generate_response"
    )

    graph.add_edge(
        "fast_track_path",
        "generate_response"
    )

    graph.add_edge(
        "standard_path",
        "generate_response"
    )

    graph.add_edge(
        "generate_response",
        "create_ticket"
    )

    graph.add_edge(
        "create_ticket",
        END
    )

    return graph.compile()


complaint_agent = build_complaint_agent()