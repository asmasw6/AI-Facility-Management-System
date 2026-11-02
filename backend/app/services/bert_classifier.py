import torch
import joblib
from pathlib import Path
from transformers import (AutoTokenizer,
                          AutoModelForSequenceClassification,
                          MarianMTModel,
                          MarianTokenizer
                        )
from model.arabic.preprocess import preprocess_arabic
from pathlib import Path

from app.services.language_service import detect_language


BASE_DIR = Path(__file__).resolve().parents[2]
print(">>>>>>>>>>>>>>>>>>>>" , BASE_DIR)

ARABIC_MODEL_PATH = BASE_DIR / "model" / "arabic"
ENGLISH_MODEL_PATH = BASE_DIR / "model" / "english"


class ComplaintClassifier:
    def __init__(self, arabic_model_path=ARABIC_MODEL_PATH,
        english_model_path=ENGLISH_MODEL_PATH):
        
        
    

         # Check model folders
        for path in [arabic_model_path, english_model_path]:
            if not Path(path).is_dir():
                raise FileNotFoundError(
                    f"Model folder not found: {Path(path).resolve()}"
                )
        
        # CPU or GPU
        self.device = torch.device(
            "cuda" if torch.cuda.is_available() else "cpu"
        )
        
        # Load Arabic model and its tokenizer
        self.arabic_path = Path(arabic_model_path)
        
        print("Loading Arabic tokenizer...")
        self.arabic_tokenizer = AutoTokenizer.from_pretrained(
            self.arabic_path
        )
        print("Loading Arabic model...")
        self.arabic_model = AutoModelForSequenceClassification.from_pretrained(
            self.arabic_path
        ).to(self.device).eval()

        # Load English model and its tokenizer
        self.english_path = Path(english_model_path)

        print("Loading English tokenizer...")
        self.english_tokenizer = AutoTokenizer.from_pretrained(
            self.english_path
        )
        print("Loading English model...")

        self.english_model = AutoModelForSequenceClassification.from_pretrained(
            self.english_path
        ).to(self.device).eval()
        
        
        # Load each model's label encoder
        self.arabic_id2label = {
            int(k): v
            for k, v in self.arabic_model.config.id2label.items()
        }
        
        
        self.english_label_encoder = joblib.load(
            self.english_path / "label_encoder.pkl")

        self.english_id2label = {
            i: str(label)
            for i, label in enumerate(
                self.english_label_encoder.classes_
            )
        }

        print("English labels:", self.english_id2label)
        
        
        print(f"Models loaded successfully on {self.device}")

        print("Arabic labels:", self.arabic_id2label)
        print("English labels:", self.english_label_encoder)
        

    def predict(self, text: str, language: str ):
        # translating Arabic first then classify
        if not text or not text.strip():
            raise ValueError("Complaint text cannot be empty")
        
        language = detect_language(text)
        
        if language == "ar":
            return self._predict(
                text, 
                self.arabic_tokenizer,
                self.arabic_model,
                self.arabic_id2label,
                language
            )
        elif language =="en":
            return self._predict(
                text,
                self.english_tokenizer,
                self.english_model,
                self.english_id2label,
                language
            )
        else:
            raise ValueError(f'Unsupported language: {language}')
        
 
    def _predict(self, text, tokenizer, model, id2label, language):
        # Apply Arabic preprocessing only to Arabic text
        if language == "ar":
            text = preprocess_arabic(text)

        if not text or not text.strip():
            raise ValueError("Text is empty after preprocessing")

        inputs = tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            padding=True,
            max_length=512
        )

        inputs = {
            key: value.to(self.device)
            for key, value in inputs.items()
        }

        with torch.no_grad():
            outputs = model(**inputs)

        probabilities = torch.softmax(outputs.logits, dim=-1)
        confidence, predicted_id = probabilities.max(dim=-1)
        category = id2label[predicted_id.item()]
        
        return category, confidence.item()
        
        
        
'''


if __name__ == "__main__":
    classifier = ComplaintClassifier( 
                                     arabic_model_path=ARABIC_MODEL_PATH,
                                     english_model_path=ENGLISH_MODEL_PATH
                                     )

    complaints = [
    
    ("بعوض كثير في الصاله ", "ar"),
    ("أريد الاستفسار عن خدمات الصيانة", "ar"),
    
    ("I need maintenance for the water heater", "en"),
    ("I would like to inquire about maintenance services", "en"),
]
    for text, language in complaints:
        try:
            result = classifier.predict(text, language=language)

            category = result["category"]
            confidence = result["confidence"]
            print("-" * 50)
            print("Complaint:", text)
            print("Language:", language)
            print("Predicted category:", category)
            print("Confidence:", round(confidence, 4))

        except Exception as exc:
            print("Error processing complaint:", text)
            print(exc)
        
'''