
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.bert_classifier import ComplaintClassifier


router = APIRouter()


# Load BERT classifier once when the API starts
try:
    classifier = ComplaintClassifier("model")
    print("BERT classifier loaded successfully!")

except Exception as e:
    classifier = None
    print(f"Failed to load BERT classifier: {e}")


class ComplaintRequest(BaseModel):
    text: str


@router.post("/predict")
def predict_complaint(request: ComplaintRequest):

    if classifier is None:
        raise HTTPException(
            status_code=503,
            detail="BERT classifier is not loaded"
        )

    try:
        category, confidence = classifier.predict(
            request.text
        )

        return {
            "text": request.text,
            "category": category,
            "confidence": confidence
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Prediction error: {str(e)}"
        )
