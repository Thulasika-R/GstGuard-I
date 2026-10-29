
import pandas as pd
import joblib

from pathlib import Path
from sklearn.ensemble import IsolationForest
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
)

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "data" / "gst_invoices.csv"
MODEL_PATH = BASE_DIR / "ml" / "gstguard_model.pkl"

# 1. Load the dataset
df = pd.read_csv(DATA_PATH)

print("Dataset loaded successfully!")
print("Dataset shape:", df.shape)

# 2. Engineer invoice consistency features
df["expected_gst"] = (
    df["taxable_value"] * df["gst_rate"] / 100
)

df["gst_difference"] = (
    df["gst_amount"] - df["expected_gst"]
).abs()

df["expected_total"] = (
    df["taxable_value"] + df["gst_amount"]
)

df["total_difference"] = (
    df["total_amount"] - df["expected_total"]
).abs()

df["expected_taxable"] = (
    df["quantity"] * df["unit_price"]
)

df["taxable_difference"] = (
    df["taxable_value"] - df["expected_taxable"]
).abs()

feature_columns = [
    "quantity",
    "unit_price",
    "taxable_value",
    "gst_rate",
    "gst_amount",
    "total_amount",
    "invoice_age_days",
    "gst_difference",
    "total_difference",
    "taxable_difference",
]

X = df[feature_columns].fillna(0)
y = df["is_anomaly"].astype(int)

# 3. Split the data for evaluation
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.25,
    random_state=42,
    stratify=y,
)

# 4. Train using only normal training invoices
X_normal = X_train[y_train == 0]

model = IsolationForest(
    n_estimators=200,
    contamination="auto",
    random_state=42,
)

model.fit(X_normal)

# 5. Predict anomalies on unseen test invoices
predictions = (model.predict(X_test) == -1).astype(int)

print("\nConfusion Matrix:")
print(confusion_matrix(y_test, predictions, labels=[0, 1]))

print("\nClassification Report:")
print(
    classification_report(
        y_test,
        predictions,
        labels=[0, 1],
        target_names=["Normal", "Anomaly"],
        zero_division=0,
    )
)

# 6. Save model and feature configuration
joblib.dump(
    {
        "model": model,
        "feature_columns": feature_columns,
    },
    MODEL_PATH,
)

print("\nModel saved successfully!")
print("Model path:", MODEL_PATH)
print("Training normal invoices:", len(X_normal))
print("Testing invoices:", len(X_test))
