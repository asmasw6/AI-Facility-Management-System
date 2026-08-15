

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime
import logging  


from database import engine, get_db, Base

from models import(
    Customer, Call, Ticket,
    CustomerCreate, CustomerResponse,
    CallCreate, CallEnd, CallResponse,
    ProcessCallRequest, TicketResponse, TicketUpdate,
    TicketStatus, TicketPriority,
)

from bert_classifier import ComplaintClassifier
#  llm service 
from llm_service import generate_llm_response

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

Base.metadata.create_all(bind=engine)
app = FastAPI(title="Facility Management Voice Assistant API")

app.add_middleware(
               CORSMiddleware,
               allow_origins=["*"], # في الإنتاج: ["https://yourdomain.com"]
               allow_credentials=True,
               allow_methods=["*"],
               allow_headers=["*"]
               )

#classifier = ComplaintClassifier = None

@app.on_event("startup")
def load_classifier():
    global classifier
    logger.info("Loading BERT classifier on startup...")
    classifier = ComplaintClassifier("model")
    logger.info("BERT classifier loaded successfully.")
    
# --------------------- >>>>>>>>>>>>>>>>>>>>>>> -----------------------------   
def determine_priority(category: str, sentiment: str, confidence: float, complaint_text: str) -> TicketPriority:
    """
    Determine the priority of a ticket based on its category.
    Adjust the logic as needed for your specific use case.
    """
    urgent_categories = {
        "Electricity Issue",
        "Security Complaint",
        "Plumbing Issue",
        "Water Supply Request",
    }

    urgent_keywords = [
        "fire",
        "smoke",
        "electrical hazard",
        "electric shock",
        "gas leak",
        "water leaking near electrical",
        "water leak near electrical",
        "flooding",
        "flood",
        "no electricity",
        "power outage",
        "elevator stuck",
        "emergency",
        "sparks",
        "short circuit",
    ]

    high_keywords = [
        "leaking",
        "water leak",
        "leakage",
        "completely stopped",
        "not working",
        "broken",
        "dangerous",
        "damage",
        "very hot",
        "no water",
    ]

    text = complaint_text.lower()

    # 1. Immediate safety/emergency issues
    if any(keyword in text for keyword in urgent_keywords):
        return TicketPriority.URGENT

    # 2. Serious facility categories
    if category in urgent_categories:
        return TicketPriority.HIGH

    # 3. Serious wording in the complaint
    if any(keyword in text for keyword in high_keywords):
        return TicketPriority.HIGH

    # 4. Customer sentiment
    if sentiment == "negative":
        return TicketPriority.MEDIUM

    # 5. Low model confidence
    if confidence < 0.5:
        return TicketPriority.MEDIUM

    return TicketPriority.LOW


# ===========================================================
#       -------------- CUSTOMER endpoints --------------
# ===========================================================
    
@app.post("/customers/", response_model=CustomerResponse)
def create_customer(customer: CustomerCreate, db: Session = Depends(get_db)):
    db_customer = Customer(**customer.model_dump())
    db.add(db_customer)
    db.commit()
    db.refresh(db_customer)
    return db_customer

    
@app.get("/customers/{customer_id}", response_model=CustomerResponse)
def get_customer(customer_id: int, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.customer_id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer


@app.get("/customers/", response_model=list[CustomerResponse])
def list_customers(db: Session = Depends(get_db)):
    return db.query(Customer).order_by(Customer.created_at.desc()).all()


# ===========================================================
#       -------------- CALL endpoints --------------
# ===========================================================
@app.post("/calls/", response_model=CallResponse)
def start_call(call: CallCreate, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.customer_id == call.customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    call = Call(customer_id=call.customer_id, transcript=call.transcript, audio_url=call.audio_url)
    db.add(call)
    db.commit()
    db.refresh(call)
    return call

@app.post("/calls/{call_id}/end", response_model=CallResponse)
def end_call(call_id: int, call_end: CallEnd, db: Session = Depends(get_db)):
    call = db.query(Call).filter(Call.call_id == call_id).first()
    if not call:
        raise HTTPException(status_code=404, detail="Call not found")
    
    call.ended_at = datetime.utcnow()
    if call_end.transcript:
        call.transcript = call_end.transcript
    if call_end.audio_url:
        call.audio_url = call_end.audio_url

    if call.started_at:
        started = call.started_at.replace(tzinfo=None) if call.started_at.tzinfo else call.started_at
        call.duration = int((call.ended_at - call.started_at).total_seconds())
    
    db.commit()
    db.refresh(call)
    return call


@app.get("/calls/{call_id}", response_model=CallResponse)
def get_call(call_id: int, db: Session = Depends(get_db)):
    call = db.query(Call).filter(Call.call_id == call_id).first()
    if not call:
        raise HTTPException(status_code=404, detail="Call not found")
    return call


# هنا لازم اسزي ملف  Bert classifer بناء علةى مودلي 


#------------------------------------------------------
from fastapi import FastAPI
from pydantic import BaseModel
from bert_classifier import ComplaintClassifier

#app = FastAPI()

# يتم تحميل BERT مرة واحدة عند تشغيل السيرفر
#classifier = ComplaintClassifier("model")


class ComplaintRequest(BaseModel):
    text: str


@app.post("/predict")
def predict_complaint(request: ComplaintRequest):

    category, confidence = classifier.predict(
        request.text
    )

    return {
        "text": request.text,
        "category": category,
        "confidence": confidence
    }

#  uvicorn main:app --reload 



async def get_sentiment_from_llm(text: str) -> str:
    """
    يرسل النص إلى الـ LLM ويطلب تصنيف المشاعر
    القيم المتوقعة: 'positive', 'negative', 'neutral'
    """
    prompt = f"""Analyze the sentiment of the following complaint and return only one word from these options:
            positive, negative, neutral

            Text: "{text}"

            Answer (one word only):"""


    try:
        response = await llm_client.chat.completions.create(
            model="your-model-name",  # عدّل حسب المزود (مثلاً gpt-4o-mini أو غيره)
            messages=[
                {
                    "role": "system",
                    "content": "You are an accurate sentiment analyzer. Reply with only one word and no explanation."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0,
            max_tokens=5
        )
        sentiment_raw = response.choices[0].message.content.strip().lower()

        # تحقق من أن القيمة ضمن القيم المسموحة، وإلا استخدم قيمة افتراضية
        valid_sentiments = {"positive", "negative", "neutral"}
        if sentiment_raw not in valid_sentiments:
            logger.warning(f"Unexpected sentiment value from LLM: {sentiment_raw}, defaulting to 'neutral'")
            return "neutral"

        return sentiment_raw

    except Exception as e:
        logger.error(f"Error during LLM sentiment analysis: {e}")
        # في حال فشل الاستدعاء، نرجّع قيمة افتراضية بدل تعطيل الطلب بالكامل
        return "neutral"

# ===========================================================
# ------------ PIPELINE -> BERT -> LLM -> Ticket------------
# ===========================================================

@app.post("/process-call", response_model=TicketResponse)
async def process_call(request: ProcessCallRequest, db: Session = Depends(get_db)):
    
    if classifier is None:
        raise HTTPException(status_code=503, detail="BERT classifier is not loaded yet")    
    
    customer = db.query(Customer).filter(Customer.customer_id == request.customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")     
    
    if request.call_id is not None:
        call = db.query(Call).filter(Call.call_id == request.call_id).first()
        if not call:
            raise HTTPException(status_code=404, detail="Call not found")          

    
    # 1) BERT: classification and confidence
    try:
        category, confidence = classifier.predict(request.text)
    except Exception as e:
        logger.error(f"Error during BERT prediction: {e}")
        raise HTTPException(status_code=500, detail="Error during BERT prediction")
    
    # 🔴🔴
    
    # 2) LLM: sentiment analysis
    sentiment = await get_sentiment_from_llm(request.text)
    print(f">>>>>>>>>>>>>> LLM sentiment analysis result: {sentiment}")
    
    priority = determine_priority(category, sentiment, confidence, request.text)
    

    # 2) LLM: Build prompt and call API
    
    ai_response = await generate_llm_response(
        complaint_text=request.text,
        category=category,
        sentiment=sentiment,
        priority=priority.value,
        building_number=customer.name,     
        apartment_number=str(request.customer_id),
    )
    # 3) save Ticket
    new_ticket = Ticket(
        customer_id=request.customer_id,
        call_id=request.call_id,
        issue_description=request.text,
        predicted_category=category,
        priority=priority,
        status=TicketStatus.OPEN,
        ai_response=ai_response,
    )
    
    db.add(new_ticket)
    db.commit()
    db.refresh(new_ticket)
    
    logger.info(f"Ticket #{new_ticket.ticket_id} created (priority={priority}).")
    return new_ticket

    











# ===========================================================
#       -------------- TICKET endpoints --------------
# ===========================================================
@app.get("/tickets", response_model=list[TicketResponse])
def list_tickets(db: Session = Depends(get_db)):
    return db.query(Ticket).order_by(Ticket.created_at.desc()).all()


@app.get("/tickets/{ticket_id}", response_model=TicketResponse)
def get_ticket(ticket_id: int, db: Session = Depends(get_db)):
    ticket = db.query(Ticket).filter(Ticket.ticket_id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="ticket not found")
    return ticket


@app.patch("/tickets/{ticket_id}", response_model=TicketResponse)
def update_ticket(ticket_id: int, payload: TicketUpdate, db: Session = Depends(get_db)):
# rr-----
    ticket = db.query(Ticket).filter(Ticket.ticket_id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="ticket not found")

    if payload.status is not None:
        ticket.status = payload.status
        if payload.status == TicketStatus.RESOLVED:
            ticket.resolved_at = datetime.utcnow()

    if payload.priority is not None:
        ticket.priority = payload.priority

    db.commit()
    db.refresh(ticket)
    return ticket


@app.get("/")
def health_check():
    return {"status": "running", "model_loaded": classifier is not None}
