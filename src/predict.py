import os
import pickle
from src.preprocessing import clean_text
from src.dataset import get_department, get_priority, get_macro_product

MODEL_PATH = "artifacts/logistic_regression_model.pkl"
VECTORIZER_PATH = "artifacts/tfidf_vectorizer.pkl"

model = None
vectorizer = None


def load_artifacts():
    global model, vectorizer
    if model is None:
        with open(MODEL_PATH, "rb") as f:
            model = pickle.load(f)
    if vectorizer is None:
        with open(VECTORIZER_PATH, "rb") as f:
            vectorizer = pickle.load(f)


def predict_complaint(text: str) -> dict:
    load_artifacts()
    cleaned = clean_text(text)
    X = vectorizer.transform([cleaned if cleaned else text])
    category = model.predict(X)[0]

    # Calculate confidence if predict_proba is available
    confidence = 0.85
    if hasattr(model, "predict_proba"):
        probs = model.predict_proba(X)[0]
        confidence = float(max(probs))

    priority = get_priority(category, text)
    department = get_department(category, text)
    macro_product = get_macro_product(category)

    return {
        "text": text,
        "cleaned_text": cleaned,
        "category": str(category),
        "macro_product": macro_product,
        "priority": priority,
        "department": department,
        "confidence": round(confidence, 4)
    }


if __name__ == "__main__":
    sample = "Someone used my debit card without my permission at a gas station and $250 was deducted."
    print("Testing complaint prediction on sample:")
    print("Complaint:", sample)
    res = predict_complaint(sample)
    for k, v in res.items():
        print(f"  {k}: {v}")