"""Generate a realistic customer purchase dataset for Task 2.

Creates ``data/customer_purchases.csv`` - a transaction-level retail dataset
covering 12 months with customer archetypes (champions, loyal, regular,
occasional, at-risk, lost) so that RFM analysis and K-Means clustering
produce meaningful, well-separated segments.

The dataset is generated with a fixed random seed, so the output is fully
reproducible. Realistic quality problems (missing values, duplicates,
invalid rows, stray whitespace) are injected deliberately so the cleaning
step in the notebook does real work.

Usage:
    python src/generate_dataset.py
"""

from __future__ import annotations

import random
from datetime import date, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

SEED = 42
random.seed(SEED)
np.random.seed(SEED)

ROOT = Path(__file__).resolve().parents[1]
OUT_PATH = ROOT / "data" / "customer_purchases.csv"

START_DATE = date(2025, 1, 1)
END_DATE = date(2025, 12, 31)

PRODUCTS = [
    ("Wireless Headphones", "Electronics", 2499),
    ("Bluetooth Speaker", "Electronics", 2999),
    ("Power Bank 20000mAh", "Electronics", 1999),
    ("Smartphone Case", "Electronics", 499),
    ("Tablet 10 inch", "Electronics", 15999),
    ("Laptop", "Electronics", 45999),
    ("Cotton Shirt", "Clothing", 899),
    ("Denim Jeans", "Clothing", 1499),
    ("Running Shoes", "Clothing", 2499),
    ("Winter Jacket", "Clothing", 2999),
    ("Saree", "Clothing", 1999),
    ("Rice Bag 5kg", "Grocery", 450),
    ("Cooking Oil 1L", "Grocery", 150),
    ("Detergent Powder", "Grocery", 210),
    ("Tea Pack 250g", "Grocery", 250),
    ("Snack Pack", "Grocery", 120),
    ("Table Lamp", "Home", 1299),
    ("Storage Box", "Home", 699),
    ("Bedsheet Set", "Home", 999),
    ("Wall Clock", "Home", 599),
    ("Yoga Mat", "Sports", 799),
    ("Dumbbell Set", "Sports", 2499),
    ("Cricket Bat", "Sports", 1999),
    ("Football", "Sports", 899),
    ("Face Cream", "Beauty", 499),
    ("Shampoo 650ml", "Beauty", 349),
    ("Perfume", "Beauty", 1299),
]

CATEGORY_AFFINITY = {
    "Electronics": 0.22,
    "Clothing": 0.18,
    "Grocery": 0.20,
    "Home": 0.12,
    "Sports": 0.14,
    "Beauty": 0.14,
}

# Each customer archetype is deliberately separated on all three RFM axes
# (frequency, recency and spend) so the segmentation step finds real groups:
#   name, weight, transactions/year, (min,max) days since last purchase,
#   active window in days (None = whole year), basket-size multiplier
ARCHETYPES = [
    {"name": "champion", "weight": 0.12, "n_txn": (14, 30), "last": (5, 45),
     "window": None, "basket": 1.70},
    {"name": "loyal", "weight": 0.17, "n_txn": (8, 14), "last": (15, 90),
     "window": None, "basket": 1.30},
    {"name": "regular", "weight": 0.20, "n_txn": (4, 7), "last": (30, 170),
     "window": None, "basket": 1.00},
    {"name": "new", "weight": 0.11, "n_txn": (1, 3), "last": (5, 45),
     "window": 60, "basket": 0.90},
    {"name": "occasional", "weight": 0.16, "n_txn": (2, 4), "last": (90, 260),
     "window": None, "basket": 0.82},
    {"name": "at_risk", "weight": 0.14, "n_txn": (3, 6), "last": (240, 330),
     "window": None, "basket": 1.15},
    {"name": "lost", "weight": 0.10, "n_txn": (1, 2), "last": (300, 360),
     "window": None, "basket": 0.72},
]

REGIONS = ["North", "South", "East", "West"]
CHANNELS = ["Online", "In-Store"]
PAYMENTS = ["UPI", "Card", "Cash", "Wallet", "COD"]


def build_customers(n_customers: int = 520) -> list[dict]:
    names = [f"CUST-{i:04d}" for i in range(1, n_customers + 1)]
    arch_names = [a["name"] for a in ARCHETYPES]
    weights = np.array([a["weight"] for a in ARCHETYPES], dtype=float)
    weights = weights / weights.sum()
    chosen = np.random.choice(arch_names, size=n_customers, p=weights)
    arch_map = {a["name"]: a for a in ARCHETYPES}

    cats = list(CATEGORY_AFFINITY.keys())
    cat_weights = np.array([CATEGORY_AFFINITY[c] for c in cats])
    cat_weights = cat_weights / cat_weights.sum()

    customers = []
    for name, arch in zip(names, chosen):
        a = arch_map[arch]
        n_txn = int(np.random.randint(a["n_txn"][0], a["n_txn"][1] + 1))
        last_offset = int(np.random.randint(a["last"][0], a["last"][1] + 1))
        last_date = END_DATE - timedelta(days=last_offset)
        window = a["window"] or (END_DATE - START_DATE).days
        activity_start = max(START_DATE, last_date - timedelta(days=window))
        customers.append(
            {
                "Customer_ID": name,
                "archetype": arch,
                "n_txn": n_txn,
                "last_date": last_date,
                "activity_start": activity_start,
                "basket_mult": float(np.random.uniform(0.9, 1.15)) * a["basket"],
                "fav_category": str(np.random.choice(cats, p=cat_weights)),
                "region": str(np.random.choice(REGIONS)),
                "channel": str(np.random.choice(CHANNELS, p=[0.55, 0.45])),
                "payment": str(np.random.choice(PAYMENTS, p=[0.38, 0.27, 0.14, 0.13, 0.08])),
            }
        )
    return customers


def build_transactions(customers: list[dict]) -> pd.DataFrame:
    rows = []
    txn_no = 100001

    for cust in customers:
        n = cust["n_txn"]
        # purchases are spread inside the customer's own activity window
        window_days = max((cust["last_date"] - cust["activity_start"]).days, 1)
        first = (cust["activity_start"] - START_DATE).days
        offsets = sorted(first + np.random.randint(0, window_days + 1, size=n))
        offsets[-1] = first + window_days  # force the last purchase date

        for off in offsets:
            txn_date = START_DATE + timedelta(days=int(off))
            # favourite category 55% of the time, otherwise any category
            if np.random.rand() < 0.55:
                pool = [p for p in PRODUCTS if p[1] == cust["fav_category"]]
            else:
                pool = PRODUCTS
            product, category, price = pool[int(np.random.randint(0, len(pool)))]

            qty = int(np.random.choice([1, 2, 3, 4, 5], p=[0.44, 0.25, 0.16, 0.09, 0.06]))
            basket = qty * price * cust["basket_mult"]
            # occasional bulk basket
            if np.random.rand() < 0.07:
                qty += int(np.random.randint(2, 6))
                basket = qty * price * cust["basket_mult"]

            discount = float(
                np.random.choice([0.0, 0.05, 0.1, 0.15, 0.2], p=[0.55, 0.18, 0.15, 0.07, 0.05])
            )
            unit_price = float(np.round(price * np.random.uniform(0.95, 1.05), 2))
            total = float(np.round(qty * unit_price * (1 - discount), 2))

            rows.append(
                {
                    "Transaction_ID": f"TXN-{txn_no}",
                    "Customer_ID": cust["Customer_ID"],
                    "Transaction_Date": txn_date.isoformat(),
                    "Product": product,
                    "Category": category,
                    "Quantity": qty,
                    "Unit_Price": unit_price,
                    "Discount": discount,
                    "Total_Amount": total,
                    "Payment_Method": cust["payment"],
                    "Region": cust["region"],
                    "Channel": cust["channel"],
                }
            )
            txn_no += 1

    df = pd.DataFrame(rows)
    df = df.sample(frac=1, random_state=SEED).reset_index(drop=True)
    return df


def inject_quality_issues(df: pd.DataFrame) -> pd.DataFrame:
    """Add realistic data-quality problems that the cleaning step must fix."""
    df = df.copy()

    # 1. stray whitespace / casing inconsistencies in text fields
    idx = np.random.choice(df.index, size=40, replace=False)
    df.loc[idx, "Channel"] = df.loc[idx, "Channel"].apply(lambda x: f" {x} ")
    idx = np.random.choice(df.index, size=30, replace=False)
    df.loc[idx, "Region"] = df.loc[idx, "Region"].apply(lambda x: f"{x} ")
    idx = np.random.choice(df.index, size=25, replace=False)
    df.loc[idx, "Payment_Method"] = df.loc[idx, "Payment_Method"].str.upper()

    # 2. missing values
    n = len(df)
    df.loc[np.random.choice(df.index, size=int(n * 0.012), replace=False), "Region"] = None
    df.loc[np.random.choice(df.index, size=int(n * 0.010), replace=False), "Payment_Method"] = None
    df.loc[np.random.choice(df.index, size=int(n * 0.008), replace=False), "Channel"] = None
    df.loc[np.random.choice(df.index, size=int(n * 0.010), replace=False), "Customer_ID"] = None
    df.loc[np.random.choice(df.index, size=int(n * 0.007), replace=False), "Transaction_Date"] = None
    df.loc[np.random.choice(df.index, size=int(n * 0.006), replace=False), "Total_Amount"] = None
    df.loc[np.random.choice(df.index, size=int(n * 0.005), replace=False), "Unit_Price"] = None

    # 3. exact duplicate rows
    dupes = df.sample(n=int(n * 0.02), random_state=SEED)
    df = pd.concat([df, dupes], ignore_index=True)

    # 4. invalid records
    bad_idx = np.random.choice(df.index, size=14, replace=False)
    df.loc[bad_idx[:6], "Quantity"] = np.random.choice([0, -1, -3], size=6)
    df.loc[bad_idx[6:10], "Total_Amount"] = np.random.choice([-150.0, -899.0, 0.0], size=4)
    df.loc[bad_idx[10:], "Discount"] = np.random.choice([1.5, -0.2, 2.0], size=4)

    # 5. a few unparseable dates
    bad_dates = np.random.choice(df.index, size=8, replace=False)
    df.loc[bad_dates, "Transaction_Date"] = ["31/02/2025", "not available", "2025-13-05",
                                              "", "TBD", "2025/99/99", "N/A", "unknown"]

    # 6. a few non-numeric amounts stored as text with currency symbol
    df["Total_Amount"] = df["Total_Amount"].astype(object)
    text_amt = np.random.choice(df.index, size=12, replace=False)
    df.loc[text_amt, "Total_Amount"] = df.loc[text_amt, "Total_Amount"].apply(
        lambda v: f"₹{v}" if pd.notna(v) else v
    )

    df = df.sample(frac=1, random_state=SEED + 1).reset_index(drop=True)
    return df


def main() -> None:
    customers = build_customers()
    df = build_transactions(customers)
    df = inject_quality_issues(df)

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT_PATH, index=False)

    print(f"Saved {OUT_PATH}")
    print(f"Rows: {len(df):,} | Customers: {df['Customer_ID'].nunique():,}")
    print(f"Columns: {', '.join(df.columns)}")


if __name__ == "__main__":
    main()
