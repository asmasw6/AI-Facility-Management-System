
from fastapi import APIRouter, HTTPException
from bson import ObjectId
from bson.errors import InvalidId

from app.database import apartments_collection, buildings_collection
from app.models.models import ApartmentCreate, ApartmentResponse


router = APIRouter()


# =========================================================
# CREATE APARTMENT
# =========================================================

@router.post("/", response_model=ApartmentResponse)
def create_apartment(apartment: ApartmentCreate):

    # Validate building ID
    try:
        building_id = ObjectId(apartment.building_id)
    except InvalidId:
        raise HTTPException(
            status_code=400,
            detail="Invalid building ID"
        )

    # Check building exists
    building = buildings_collection.find_one({
        "_id": building_id
    })

    if not building:
        raise HTTPException(
            status_code=404,
            detail="Building not found"
        )

    # Check apartment doesn't already exist in this building
    existing_apartment = apartments_collection.find_one({
        "building_id": building_id,
        "apartment_number": apartment.apartment_number.value
    })

    if existing_apartment:
        raise HTTPException(
            status_code=400,
            detail="Apartment already exists in this building"
        )

    apartment_data = {
        "apartment_number": apartment.apartment_number.value,
        "building_id": building_id
    }

    result = apartments_collection.insert_one(apartment_data)

    created_apartment = apartments_collection.find_one({
        "_id": result.inserted_id
    })

    created_apartment["_id"] = str(created_apartment["_id"])
    created_apartment["building_id"] = str(
        created_apartment["building_id"]
    )

    return created_apartment


# =========================================================
# GET ALL APARTMENTS
# =========================================================

@router.get("/", response_model=list[ApartmentResponse])
def get_apartments():

    apartments = list(apartments_collection.find())

    for apartment in apartments:
        apartment["_id"] = str(apartment["_id"])
        apartment["building_id"] = str(apartment["building_id"])

    return apartments


# =========================================================
# GET APARTMENTS BY BUILDING
# =========================================================

@router.get("/building/{building_id}", response_model=list[ApartmentResponse])
def get_apartments_by_building(building_id: str):

    try:
        object_id = ObjectId(building_id)
    except InvalidId:
        raise HTTPException(
            status_code=400,
            detail="Invalid building ID"
        )

    apartments = list(
        apartments_collection.find({
            "building_id": object_id
        })
    )

    for apartment in apartments:
        apartment["_id"] = str(apartment["_id"])
        apartment["building_id"] = str(apartment["building_id"])

    return apartments


# =========================================================
# GET APARTMENT BY ID
# =========================================================

@router.get("/{apartment_id}", response_model=ApartmentResponse)
def get_apartment(apartment_id: str):

    try:
        object_id = ObjectId(apartment_id)
    except InvalidId:
        raise HTTPException(
            status_code=400,
            detail="Invalid apartment ID"
        )

    apartment = apartments_collection.find_one({
        "_id": object_id
    })

    if not apartment:
        raise HTTPException(
            status_code=404,
            detail="Apartment not found"
        )

    apartment["_id"] = str(apartment["_id"])
    apartment["building_id"] = str(apartment["building_id"])

    return apartment
