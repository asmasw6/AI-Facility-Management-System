
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.buildings import router as buildings_router
from app.routes.apartments import router as apartments_router
from app.routes.customers import router as customers_router
from app.routes.calls import router as calls_router
from app.routes.tickets import router as tickets_router
from app.routes.ai import router as ai_router
from app.routes.process_call import router as process_call_router

app = FastAPI(
    title="AI Facility Management System",
    description="AI-powered facility management and customer support API",
    version="1.0.0"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



app.include_router(
    buildings_router,
    prefix="/api/buildings",
    tags=["Buildings"]
)

app.include_router(
    apartments_router,
    prefix="/api/apartments",
    tags=["Apartments"]
)

app.include_router(
    customers_router,
    prefix="/api/customers",
    tags=["Customers"]
)


app.include_router(
    calls_router,
    prefix="/api/calls",
    tags=["Calls"]
)


app.include_router(
    tickets_router,
    prefix="/api/tickets",
    tags=["Tickets"]
)


app.include_router(
    ai_router,
    prefix="/api/ai",
    tags=["AI"]
)

app.include_router(
    process_call_router,
    prefix="/api/process-call",
    tags=["Process Call"]
)



@app.get("/")
def root():
    return {
        "message": "AI Facility Management System API",
        "status": "running",
        "version": "1.0.0"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }
