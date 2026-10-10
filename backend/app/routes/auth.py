from fastapi import APIRouter, HTTPException
from bson import ObjectId

from app.models.models import CustomerRegister, CustomerLogin, CustomerResponse, LoginResponse
from app.utils.security import hash_password, verify_password, create_access_token
from app.database import customers_collection, apartments_collection
from app.models.models  import RegistrationStatus
from datetime import datetime, timezone

router = APIRouter()

@router.post("/register")
async def register_customer(customer: CustomerRegister):

    # Check if email already exists
    existing_customer = customers_collection.find_one({
        "email": customer.email
    })

    if existing_customer:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    # 🔴🔴🔴🔴🔴🔴🔴🔴🔴🔴🔴🔴🔴🔴🔴
    # Find apartment
    apartment = apartments_collection.find_one({
        "apartment_code": customer.apartment_code,
        "registration_code": customer.registration_code,
        "registration_status": RegistrationStatus.AVAILABLE.value   
    })

    if not apartment:
        raise HTTPException(
            status_code=404,
            detail="Invalid apartment code or registration code"
        )


    # Check if apartment already has a customer
    existing_resident = customers_collection.find_one({
        "apartment_id": str(apartment["_id"])
    })

    if existing_resident:
        raise HTTPException(
            status_code=400,
            detail="This apartment is already registered"
        )


    # Hash password
    password_hash = hash_password(
        customer.password
    )


    # Create customer
    customer_document = {
        "name": customer.name,
        "phone": customer.phone,
        "email": customer.email,
        "password": password_hash,
        "apartment_id": apartment["_id"],
        "created_at": datetime.now(timezone.utc)
    }


    result = customers_collection.insert_one(
        customer_document
    )
    
    # make apartment registration status to REGISTERED
    apartments_collection.update_one(
        {"_id": apartment["_id"]},
        {"$set": {"registration_status": RegistrationStatus.REGISTERED.value}}
    )
    
    # created customer
    created_customer = customers_collection.find_one({
        "_id": result.inserted_id
    })
    
    created_customer["_id"] = str(created_customer["_id"])
    created_customer["apartment_id"] = str(created_customer["apartment_id"])
    
    
    return {
        "message": "Registration successful",
        "customer_id": created_customer #str(result.inserted_id)
    }
    
    
    
@router.post("/login", response_model=LoginResponse)
async def login_customer(credentials: CustomerLogin):
    
    customer = customers_collection.find_one({
        "email": credentials.email
    })

    if not customer:
        raise HTTPException(
            status_code=401,
            detail="Invalid email"
        )


    password_valid = verify_password(
        credentials.password,
        customer["password"]
    )

    if not password_valid:
        raise HTTPException(
            status_code=401,
            detail="Invalid password"
        )


    # Create JWT
    access_token = create_access_token({
        "customer_id": str(
            customer["_id"]
        ),
        "apartment_id": str(customer[
            "apartment_id"
        ])
    })
    
    customer_response = {
        "_id": str(customer["_id"]),
        "name": customer["name"],
        "phone": customer.get("phone"),
        "email": customer.get("email"),
        "apartment_id": str(
            customer["apartment_id"]
        ),
        "created_at": customer["created_at"]
    }
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "customer": customer_response
    }
    
