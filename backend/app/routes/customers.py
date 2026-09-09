
from fastapi import APIRouter, HTTPException
from bson import ObjectId
from bson.errors import InvalidId
from datetime import datetime, timezone

from app.database import customers_collection, apartments_collection
from app.models.models import CustomerCreate, CustomerResponse

router = APIRouter()


# Create Customer
@router.post("/", response_model=CustomerResponse)
def create_customer(customer: CustomerCreate):

    # Validate apartment_id
    try:
        apartment_id = ObjectId(customer.apartment_id)
    except InvalidId:
        raise HTTPException(
            status_code=400,
            detail="Invalid apartment ID"
        )

    # Check apartment exists
    apartment = apartments_collection.find_one({
        "_id": apartment_id
    })

    if not apartment:
        raise HTTPException(
            status_code=404,
            detail="Apartment not found"
        )

    # Check if phone already exists
    if customer.phone:
        existing_customer = customers_collection.find_one({
            "phone": customer.phone
        })

        if existing_customer:
            raise HTTPException(
                status_code=400,
                detail="Customer with this phone already exists"
            )

    customer_data = {
        "name": customer.name,
        "phone": customer.phone,
        "email": customer.email,
        "apartment_id": apartment_id,
        "created_at": datetime.now(timezone.utc)
    }

    result = customers_collection.insert_one(customer_data)

    created_customer = customers_collection.find_one({
        "_id": result.inserted_id
    })

    # Convert ObjectId to string
    created_customer["_id"] = str(created_customer["_id"])
    created_customer["apartment_id"] = str(
        created_customer["apartment_id"]
    )

    return created_customer


# Get All Customers
@router.get("/", response_model=list[CustomerResponse])
def get_customers():

    customers = list(
        customers_collection.find()
    )

    for customer in customers:
        customer["_id"] = str(customer["_id"])
        customer["apartment_id"] = str(
            customer["apartment_id"]
        )

    return customers


# Get Customer by ID
@router.get("/{customer_id}", response_model=CustomerResponse)
def get_customer(customer_id: str):

    try:
        object_id = ObjectId(customer_id)
    except InvalidId:
        raise HTTPException(
            status_code=400,
            detail="Invalid customer ID"
        )

    customer = customers_collection.find_one({
        "_id": object_id
    })

    if not customer:
        raise HTTPException(
            status_code=404,
            detail="Customer not found"
        )

    customer["_id"] = str(customer["_id"])
    customer["apartment_id"] = str(
        customer["apartment_id"]
    )

    return customer


# Get Customers by Apartment
@router.get(
    "/apartment/{apartment_id}",
    response_model=list[CustomerResponse]
)
def get_customers_by_apartment(apartment_id: str):

    try:
        object_id = ObjectId(apartment_id)
    except InvalidId:
        raise HTTPException(
            status_code=400,
            detail="Invalid apartment ID"
        )

    customers = list(
        customers_collection.find({
            "apartment_id": object_id
        })
    )

    for customer in customers:
        customer["_id"] = str(customer["_id"])
        customer["apartment_id"] = str(
            customer["apartment_id"]
        )

    return customers
