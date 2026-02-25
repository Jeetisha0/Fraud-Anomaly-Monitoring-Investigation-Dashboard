# ======================================================
# Part-B:  Data Architecture & ETL Pipeline
#  1: Load Raw Data
# ======================================================

import pandas as pd
import os

# -------------------------------
# Define raw data path
# -------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_PATH = os.path.join(BASE_DIR, "raw")

print("Loading raw datasets...\n")

# -------------------------------
# Load CSV files
# -------------------------------
users = pd.read_csv(os.path.join(RAW_PATH, "users.csv"))
sessions = pd.read_csv(os.path.join(RAW_PATH, "sessions.csv"))
orders = pd.read_csv(os.path.join(RAW_PATH, "orders.csv"))
order_items = pd.read_csv(os.path.join(RAW_PATH, "order_items.csv"))
payments = pd.read_csv(os.path.join(RAW_PATH, "payments.csv"))
refunds = pd.read_csv(os.path.join(RAW_PATH, "refunds.csv"))
shipments = pd.read_csv(os.path.join(RAW_PATH, "shipments.csv"))
coupons = pd.read_csv(os.path.join(RAW_PATH, "coupons.csv"))

# -------------------------------
# Load JSON file
# -------------------------------
products = pd.read_json(os.path.join(RAW_PATH, "products.json"))

# -------------------------------
# Print dataset shapes
# -------------------------------
print("Users:", users.shape)
print("Sessions:", sessions.shape)
print("Orders:", orders.shape)
print("Order Items:", order_items.shape)
print("Payments:", payments.shape)
print("Refunds:", refunds.shape)
print("Shipments:", shipments.shape)
print("Coupons:", coupons.shape)
print("Products:", products.shape)

print("\nAll datasets loaded successfully.")

# ======================================================
#  2: Data Cleaning
# ======================================================

print("\nStarting data cleaning...")

# -------------------------------
# Remove duplicates based on primary keys
# -------------------------------

users = users.drop_duplicates(subset=["user_id"])
sessions = sessions.drop_duplicates(subset=["session_id"])
orders = orders.drop_duplicates(subset=["order_id"])
order_items = order_items.drop_duplicates()
payments = payments.drop_duplicates()
refunds = refunds.drop_duplicates()
shipments = shipments.drop_duplicates()
coupons = coupons.drop_duplicates(subset=["coupon_id"])

print("Duplicates removed.")

# -------------------------------
# Standardize text casing
# -------------------------------

if "payment_method" in payments.columns:
    payments["payment_method"] = payments["payment_method"].str.lower()

if "shipping_city" in shipments.columns:
    shipments["shipping_city"] = shipments["shipping_city"].str.lower()

if "shipping_pincode" in shipments.columns:
    shipments["shipping_pincode"] = shipments["shipping_pincode"].astype(str)

print("Text casing standardized.")

# -------------------------------
# Handle missing values
# -------------------------------

# If coupon is missing, assume no coupon used
if "coupon_id" in orders.columns:
    orders["coupon_id"] = orders["coupon_id"].fillna("NO_COUPON")

# If discount missing, assume 0
if "discount_amount" in orders.columns:
    orders["discount_amount"] = orders["discount_amount"].fillna(0)

# Fill missing payment method as unknown
if "payment_method" in payments.columns:
    payments["payment_method"] = payments["payment_method"].fillna("unknown")

print("Missing values handled.")

# -------------------------------
# Convert timestamp columns to datetime
# -------------------------------

if "order_ts" in orders.columns:
    orders["order_ts"] = pd.to_datetime(orders["order_ts"], errors="coerce")

if "session_ts" in sessions.columns:
    sessions["session_ts"] = pd.to_datetime(sessions["session_ts"], errors="coerce")

if "shipment_ts" in shipments.columns:
    shipments["shipment_ts"] = pd.to_datetime(shipments["shipment_ts"], errors="coerce")

print("Timestamps converted to datetime.")

print("\nCleaning complete.")
print("Orders null check:\n", orders.isnull().sum().head())

# ======================================================
#  3A — Aggregate order_items
# ======================================================

print("\nAggregating order_items...")

# Join products to get category
order_items = order_items.merge(
    products[["product_id", "category"]],
    on="product_id",
    how="left"
)

# Aggregate
order_items_agg = (
    order_items
    .groupby("order_id")
    .agg(
        item_count=("product_id", "count"),
        total_qty=("quantity", "sum"),
        top_category=("category", lambda x: x.mode().iloc[0] if not x.mode().empty else None)
    )
    .reset_index()
)

print("order_items aggregation complete:", order_items_agg.shape)

# ======================================================
#  3B — Aggregate payments
# ======================================================

print("\nAggregating payments...")

# Assume payment_status column exists (adjust if different)
if "payment_status" in payments.columns:

    payments_agg = (
        payments
        .groupby("order_id")
        .agg(
            payment_fail_count_before_success=(
                "payment_status",
                lambda x: (x == "failed").sum()
            ),
            payment_method=("payment_method", "last")
        )
        .reset_index()
    )

else:
    payments_agg = payments.groupby("order_id").size().reset_index(name="payment_attempts")

print("payments aggregation complete:", payments_agg.shape)

# ======================================================
#  3C — Device reuse count
# ======================================================

print("\nCalculating device reuse...")

if "device_id" in sessions.columns:

    device_counts = (
        sessions
        .groupby("device_id")
        .agg(device_reuse_count=("user_id", "nunique"))
        .reset_index()
    )

    sessions = sessions.merge(device_counts, on="device_id", how="left")

print("Device reuse calculated.")