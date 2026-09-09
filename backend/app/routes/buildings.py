
from fastapi import APIRouter, HTTPException
from app.database import buildings_collection
from app.models.models import BuildingCreate, BuildingResponse


router = APIRouter()


# =========================================================
# CREATE BUILDING
# =========================================================

@router.post("/", response_model=BuildingResponse)
def create_building(building: BuildingCreate):

    # Check if building already exists
    existing_building = buildings_collection.find_one({
        "building_name": building.building_name.value
    })

    if existing_building:
        raise HTTPException(
            status_code=400,
            detail="Building already exists"
        )

    building_data = building.model_dump()

    building_data["building_name"] = building.building_name.value

    result = buildings_collection.insert_one(building_data)

    created_building = buildings_collection.find_one({
        "_id": result.inserted_id
    })

    created_building["_id"] = str(created_building["_id"])

    return created_building


# =========================================================
# GET ALL BUILDINGS
# =========================================================

@router.get("/" )  # response_model=list[BuildingResponse]
def get_buildings():

    buildings = list(buildings_collection.find())

    for building in buildings:
        building["_id"] = str(building["_id"])

    return buildings


# =========================================================
# GET BUILDING BY ID
# =========================================================
@router.get("/{building_id}", response_model=BuildingResponse)
def get_building(building_id: str):

    from bson import ObjectId
    from bson.errors import InvalidId

    try:
        object_id = ObjectId(building_id)
    except InvalidId:
        raise HTTPException(
            status_code=400,
            detail="Invalid building ID"
        )

    building = buildings_collection.find_one({
        "_id": object_id
    })

    if not building:
        raise HTTPException(
            status_code=404,
            detail="Building not found"
        )

    building["_id"] = str(building["_id"])

    return building
