
import numpy as np
import pandas as pd
from pathlib import Path

# Reproducible synthetic invoice data
rng = np.random.default_rng(42)

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

NUM_INVOICES = 2000
NUM_SHOPS = 100

shop_ids = [f"SHOP{i:03d}" for i in range(1, NUM_SHOPS + 1)]
shop_id = rng.choice(shop_ids, NUM_INVOICES)

quantity = rng.integers(1, 101, NUM_INVOICES)
unit_price = np.round(rng.uniform(100, 10000, NUM_INVOICES), 2)
taxable_value = np.round(quantity * unit_price, 2)
gst_rate = rng.choice([0, 5, 12, 18, 28], NUM_INVOICES)

gst_amount = np.round(taxable_value * gst_rate / 100, 2)
total_amount = np.round(taxable_value + gst_amount, 2)

df = pd.DataFrame({
    "invoice_id": [f"INV{i:05d}" for i in range(1, NUM_INVOICES + 1)],
    "shop_id": shop_id,
    "quantity": quantity,
    "unit_price": unit_price,
    "taxable_value": taxable_value,
    "gst_rate": gst_rate,
    "gst_amount": gst_amount,
    "total_amount": total_amount,
    "invoice_age_days": rng.integers(0, 366, NUM_INVOICES),
})

# Introduce controlled anomalies for prototype training and testing
df["is_anomaly"] = 0
anomaly_indices = rng.choice(
    df.index, size=int(NUM_INVOICES * 0.08), replace=False
)

for idx in anomaly_indices:
    anomaly_type = rng.choice([
        "incorrect_gst",
        "incorrect_total",
        "unusual_price",
        "unusual_quantity",
    ])

    if anomaly_type == "incorrect_gst":
        df.loc[idx, "gst_amount"] = round(
            df.loc[idx, "taxable_value"]
            * df.loc[idx, "gst_rate"] / 100 * 1.5, 2
        )

    elif anomaly_type == "incorrect_total":
        df.loc[idx, "total_amount"] = round(
            df.loc[idx, "taxable_value"]
            + df.loc[idx, "gst_amount"] + 5000, 2
        )

    elif anomaly_type == "unusual_price":
        df.loc[idx, "unit_price"] = round(
            df.loc[idx, "unit_price"] * 10, 2
        )

    else:
        df.loc[idx, "quantity"] = int(
            df.loc[idx, "quantity"] * 10
        )

    df.loc[idx, "is_anomaly"] = 1

output_path = DATA_DIR / "gst_invoices.csv"
df.to_csv(output_path, index=False)

print("Dataset generated successfully!")
print(f"Saved to: {output_path}")
print(f"Total invoices: {len(df)}")
print(f"Normal invoices: {(df['is_anomaly'] == 0).sum()}")
print(f"Anomalous invoices: {(df['is_anomaly'] == 1).sum()}")
print("\nSample records:")
print(df.head())
