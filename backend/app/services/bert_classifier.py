import torch
import joblib
from pathlib import Path
from transformers import AutoTokenizer, AutoModelForSequenceClassification


class ComplaintClassifier:
    def __init__(self, model_path: str = "model"):
        self.model_path = Path(model_path)

        # Load tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(
            self.model_path
        )

        # Load fine-tuned BERT model
        self.model = AutoModelForSequenceClassification.from_pretrained(
            self.model_path
        )

        # Load LabelEncoder
        self.label_encoder = joblib.load(
            self.model_path / "label_encoder.pkl"
        )

        # CPU or GPU
        self.device = torch.device(
            "cuda" if torch.cuda.is_available() else "cpu"
        )

        self.model.to(self.device)
        self.model.eval()

    def predict(self, text: str):
        # Tokenize text
        inputs = self.tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            padding=True,
            max_length=512
        )

        # Move tensors to device
        inputs = {
            key: value.to(self.device)
            for key, value in inputs.items()
        }

        # Prediction
        with torch.no_grad():
            outputs = self.model(**inputs)

        # Convert logits to probabilities
        probabilities = torch.softmax(
            outputs.logits,
            dim=-1
        )

        confidence, predicted_id = torch.max(
            probabilities,
            dim=-1
        )

        predicted_id = predicted_id.item()
        confidence = confidence.item()

        # Convert ID → Category
        category = self.label_encoder.inverse_transform(
            [predicted_id]
        )[0]

        return category, confidence

'''
if __name__ == "__main__":
    classifier = ComplaintClassifier("model")

    text = (
        "The air conditioner is leaking water "
        "and is no longer cooling the apartment."
    )

    category, confidence = classifier.predict(text)

    print("Category:", category)
    print("Confidence:", round(confidence, 4))
    
'''