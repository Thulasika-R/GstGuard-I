
from pathlib import Path

import joblib
import pandas as pd

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field


BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = BASE_DIR / "ml" / "gstguard_model.pkl"

app = FastAPI(
    title="GstGuard-I API",
    description="GST invoice anomaly detection",
    version="1.0.0",
)



app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5176",
        "http://127.0.0.1:5176",
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


# Load the trained model
model_bundle = None

try:
    model_bundle = joblib.load(MODEL_PATH)
    print("GstGuard-I model loaded successfully!")
except FileNotFoundError:
    print(f"Trained model not found: {MODEL_PATH}")


class InvoiceRequest(BaseModel):
    invoice_id: str = Field(min_length=1, max_length=100)
    shop_id: str = Field(min_length=1, max_length=100)
    quantity: float = Field(gt=0, le=1_000_000)
    unit_price: float = Field(ge=0, le=1_000_000_000)
    taxable_value: float = Field(ge=0, le=1_000_000_000_000)
    gst_rate: float = Field(ge=0, le=100)
    gst_amount: float = Field(ge=0, le=1_000_000_000_000)
    total_amount: float = Field(ge=0, le=1_000_000_000_000)
    invoice_age_days: int = Field(ge=0, le=36500)


@app.get("/")
def home():
    return {
        "project": "GstGuard-I",
        "status": "success",
        "message": "Backend is running",
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "model_loaded": model_bundle is not None,
    }

@app.get("/api/health")
def api_health_check():
    return {
        "status": "healthy",
        "model_loaded": model_bundle is not None,
    }


@app.post("/predict")
def predict_invoice(invoice: InvoiceRequest):
    if model_bundle is None:
        raise HTTPException(
            status_code=503,
            detail="Trained model is unavailable. Train the model first.",
        )

    data = invoice.model_dump()

    expected_gst = data["taxable_value"] * data["gst_rate"] / 100
    expected_total = data["taxable_value"] + data["gst_amount"]
    expected_taxable = data["quantity"] * data["unit_price"]

    features = {
        "quantity": data["quantity"],
        "unit_price": data["unit_price"],
        "taxable_value": data["taxable_value"],
        "gst_rate": data["gst_rate"],
        "gst_amount": data["gst_amount"],
        "total_amount": data["total_amount"],
        "invoice_age_days": data["invoice_age_days"],
        "gst_difference": abs(data["gst_amount"] - expected_gst),
        "total_difference": abs(data["total_amount"] - expected_total),
        "taxable_difference": abs(
            data["taxable_value"] - expected_taxable
        ),
    }

    feature_columns = model_bundle["feature_columns"]
    X = pd.DataFrame([features])[feature_columns]

    model = model_bundle["model"]
    prediction = int(model.predict(X)[0])
    anomaly_score = float(model.decision_function(X)[0])

    issues = []

    if abs(data["gst_amount"] - expected_gst) > 1.0:
        issues.append("GST amount differs from the calculated amount.")

    if abs(data["total_amount"] - expected_total) > 1.0:
        issues.append("Invoice total does not match taxable value plus GST.")

    if abs(data["taxable_value"] - expected_taxable) > 1.0:
        issues.append("Taxable value does not match quantity multiplied by unit price.")

    if prediction == -1:
        status = "SUSPICIOUS"
        message = "The model detected an unusual invoice pattern."
    else:
        status = "NORMAL"
        message = "The model did not detect an unusual pattern."

    if issues:
        status = "SUSPICIOUS"
        message = "Invoice arithmetic inconsistencies require review."

    return {
        "invoice_id": data["invoice_id"],
        "shop_id": data["shop_id"],
        "status": status,
        "model_prediction": "ANOMALY" if prediction == -1 else "NORMAL",
        "anomaly_score": round(anomaly_score, 6),
        "issues": issues,
        "message": message,
        "disclaimer": (
            "This is an automated screening result, not proof of fraud "
            "or a determination of GST compliance."
        ),
    }
