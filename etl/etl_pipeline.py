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

payments_agg = (
    payments
    .groupby("order_id")
    .agg(
        payment_fail_count_before_success=(
            "payment_status",
            lambda x: (x == "failed").sum()
        ),
        payment_method=("payment_method", "last")  # keep final method
    )
    .reset_index()
)

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

# ======================================================
#  4 — Build fact_orders_enriched
# ======================================================

print("\nBuilding fact_orders_enriched...")

# Start from orders (base table)
fact_orders = orders.copy()

# -------------------------------
# Join users
# -------------------------------
fact_orders = fact_orders.merge(
    users,
    on="user_id",
    how="left"
)

# -------------------------------
# Join sessions
# -------------------------------
fact_orders = fact_orders.merge(
    sessions[["session_id", "device_id", "device_reuse_count"]],
    on="session_id",
    how="left"
)

# -------------------------------
# Join shipments
# -------------------------------
fact_orders = fact_orders.merge(
    shipments[["order_id"]],
    on="order_id",
    how="left"
)

# -------------------------------
# Join refunds
# -------------------------------
fact_orders = fact_orders.merge(
    refunds[["order_id"]],
    on="order_id",
    how="left",
    indicator=True
)

# Create refund flag
fact_orders["refund_flag"] = fact_orders["_merge"].apply(
    lambda x: 1 if x == "both" else 0
)

fact_orders.drop(columns=["_merge"], inplace=True)

# -------------------------------
# Join coupons
# -------------------------------
fact_orders = fact_orders.merge(
    coupons,
    on="coupon_id",
    how="left"
)

# -------------------------------
# Join aggregated order_items
# -------------------------------
fact_orders = fact_orders.merge(
    order_items_agg,
    on="order_id",
    how="left"
)

# -------------------------------
# Join aggregated payments
# -------------------------------
fact_orders = fact_orders.merge(
    payments_agg,
    on="order_id",
    how="left"
)

print("fact_orders_enriched built:", fact_orders.shape) 


# -------------------------------
# Monetary fields
# -------------------------------

if "gross_amount" not in fact_orders.columns:
    if "order_amount" in fact_orders.columns:
        fact_orders["gross_amount"] = fact_orders["order_amount"]

if "discount_amount" not in fact_orders.columns:
    fact_orders["discount_amount"] = 0

fact_orders["net_amount"] = (
    fact_orders["gross_amount"] - fact_orders["discount_amount"]
)


# -------------------------------
# Derive shipping_city_tier (simple rule)
# -------------------------------

metro_pincodes = ["400", "110", "560", "600"]  # example prefixes

fact_orders["shipping_city_tier"] = fact_orders["shipping_pincode"].astype(str).apply(
    lambda x: "Tier 1" if any(x.startswith(prefix) for prefix in metro_pincodes) else "Tier 2/3"
)

print(fact_orders.head())
print(fact_orders.shape)

# --------------------------------------------------
# Ensure ONE row per order (remove duplicates safely)
# --------------------------------------------------

fact_orders = fact_orders.sort_values("order_ts")

fact_orders = fact_orders.drop_duplicates(
    subset=["order_id"],
    keep="last"
)

print("\nAfter removing duplicates:")
print("Rows:", fact_orders.shape[0])
print("Unique orders:", fact_orders["order_id"].nunique())

# ======================================================
# Step 5 — Risk Signals
# ======================================================

print("\nCreating risk signals...")

# Calculate discount percentage
fact_orders["coupon_discount_pct"] = (
    fact_orders["discount_amount"] / fact_orders["gross_amount"]
).fillna(0)

fact_orders["high_discount_flag"] = (
    fact_orders["coupon_discount_pct"] >= 0.30
).astype(int)

# new user flag
if "user_created_ts" in fact_orders.columns:

    fact_orders["account_age_days"] = (
        fact_orders["order_ts"] - fact_orders["user_created_ts"]
    ).dt.days

    fact_orders["new_user_flag"] = (
        fact_orders["account_age_days"] <= 7
    ).astype(int)
else:
    fact_orders["new_user_flag"] = 0

print("\nColumns available in fact_orders:")
print(fact_orders.columns.tolist())

# Cash-on-Delivery (COD) Flag
# Only create flag if payment_method exists

if "payment_method" in fact_orders.columns:
    fact_orders["cod_flag"] = (
        fact_orders["payment_method"].str.lower() == "cod"
    ).astype(int)
else:
    fact_orders["cod_flag"] = 0

#late night order flag
# Extract hour from order timestamp
fact_orders["order_hour"] = pd.to_datetime(fact_orders["order_ts"]).dt.hour

fact_orders["late_night_order_flag"] = (
    (fact_orders["order_hour"] >= 23) | (fact_orders["order_hour"] <= 5)
).astype(int)

#quantity outlier flag
fact_orders["qty_outlier_flag"] = (
    fact_orders["total_qty"] >
    fact_orders["total_qty"].quantile(0.95)
).astype(int)

#pincode reuse count
pincode_counts = (
    fact_orders.groupby("shipping_pincode")["user_id"]
    .nunique()
    .reset_index(name="pincode_reuse_count")
)

fact_orders = fact_orders.merge(
    pincode_counts,
    on="shipping_pincode",
    how="left"
)

#multi coupon user flag
coupon_usage = (
    fact_orders.groupby("user_id")["coupon_id"]
    .nunique()
    .reset_index(name="coupon_variety")
)

fact_orders = fact_orders.merge(
    coupon_usage,
    on="user_id",
    how="left"
)

fact_orders["multi_coupon_user_flag"] = (
    fact_orders["coupon_variety"] > 3
).astype(int)

# payment failure signal
fact_orders["payment_fail_count_before_success"] = (
    fact_orders["payment_fail_count_before_success"]
    .fillna(0)
)

# order value Z-score by category
fact_orders["order_value_zscore_by_category"] = (
    fact_orders.groupby("top_category")["net_amount"]
    .transform(lambda x: (x - x.mean()) / x.std())
).fillna(0)

print(fact_orders.columns.tolist())

# ======================================================
# Step 6 — Risk Scoring System
# ======================================================

print("\nCalculating risk score...")

# Initialize risk score
fact_orders["risk_score"] = 0

# ------------------------------------------------------
# Add weighted signals
# ------------------------------------------------------

# High discount abuse
fact_orders["risk_score"] += fact_orders["high_discount_flag"] * 15

# New user risk
fact_orders["risk_score"] += fact_orders["new_user_flag"] * 10

# COD risk
fact_orders["risk_score"] += fact_orders["cod_flag"] * 10

# Late night behaviour
fact_orders["risk_score"] += fact_orders["late_night_order_flag"] * 5

# Quantity anomaly
fact_orders["risk_score"] += fact_orders["qty_outlier_flag"] * 10

# Device reuse
fact_orders["risk_score"] += (
    fact_orders["device_reuse_count"] > 3
).astype(int) * 15

# Payment failures
fact_orders["risk_score"] += (
    fact_orders["payment_fail_count_before_success"] > 2
).astype(int) * 20

# Multi coupon users
fact_orders["risk_score"] += fact_orders["multi_coupon_user_flag"] * 10

# Extreme order value anomaly
fact_orders["risk_score"] += (
    abs(fact_orders["order_value_zscore_by_category"]) > 2
).astype(int) * 15


# ------------------------------------------------------
# Assign Risk Band
# ------------------------------------------------------
# ------------------------------------------------
# Create Risk Bands using ranking (stable method)
# ------------------------------------------------

# Rank orders by risk_score
fact_orders["risk_rank"] = fact_orders["risk_score"].rank(method="first")

# Total number of orders
n = len(fact_orders)

def assign_risk_band(rank):
    if rank >= n * 0.80:
        return "High"
    elif rank >= n * 0.50:
        return "Medium"
    else:
        return "Low"

fact_orders["risk_band"] = fact_orders["risk_rank"].apply(assign_risk_band)

# Drop helper column
fact_orders.drop(columns=["risk_rank"], inplace=True)

print("Risk scoring complete.")


# ======================================================
# Step 7 — Create Investigation Queue
# ======================================================

print("\nBuilding investigation queue...")

# ------------------------------------------------------
# Define function to extract top 3 risk reasons
# ------------------------------------------------------

def get_risk_reasons(row):
    reasons = []

    if row["high_discount_flag"] == 1:
        reasons.append("High discount usage")

    if row["new_user_flag"] == 1:
        reasons.append("New user account")

    if row["cod_flag"] == 1:
        reasons.append("Cash on delivery order")

    if row["late_night_order_flag"] == 1:
        reasons.append("Late night order")

    if row["qty_outlier_flag"] == 1:
        reasons.append("Unusual quantity")

    if row["multi_coupon_user_flag"] == 1:
        reasons.append("Multiple coupon usage")

    if row["payment_fail_count_before_success"] > 2:
        reasons.append("Multiple payment failures")

    if row["device_reuse_count"] > 3:
        reasons.append("Device reused across users")

    if abs(row["order_value_zscore_by_category"]) > 2:
        reasons.append("Order value anomaly")

    return ", ".join(reasons[:3])  # Top 3 only


fact_orders["top_3_risk_reasons"] = fact_orders.apply(get_risk_reasons, axis=1)


# ------------------------------------------------------
# Recommended Action Logic
# ------------------------------------------------------

def recommend_action(row):
    if row["risk_band"] == "High":
        return "Hold for manual review"
    elif row["risk_band"] == "Medium":
        return "Call verification"
    else:
        return "Auto process"

fact_orders["recommended_action"] = fact_orders.apply(recommend_action, axis=1)


# ------------------------------------------------------
# Evidence Fields (What triggered risk)
# ------------------------------------------------------

fact_orders["evidence_fields"] = (
    "discount_pct=" + fact_orders["coupon_discount_pct"].round(2).astype(str)
    + "; payment_failures=" + fact_orders["payment_fail_count_before_success"].astype(str)
    + "; device_reuse=" + fact_orders["device_reuse_count"].astype(str)
    + "; total_qty=" + fact_orders["total_qty"].astype(str)
)


# ------------------------------------------------------
# Final Investigation Queue Table
# ------------------------------------------------------

investigation_queue = fact_orders[
    [
        "order_id",
        "risk_score",
        "risk_band",
        "top_3_risk_reasons",
        "recommended_action",
        "evidence_fields"
    ]
].sort_values("risk_score", ascending=False)


print("Investigation queue created:", investigation_queue.shape)


# ======================================================
# Step 8 — Create fact_user_risk_weekly
# ======================================================

print("\nBuilding weekly user risk table...")

# ------------------------------------------------------
# Create week_start column
# ------------------------------------------------------

fact_orders["week_start"] = (
    fact_orders["order_ts"]
    .dt.to_period("W")
    .apply(lambda r: r.start_time)
)

# ------------------------------------------------------
# Aggregate weekly metrics
# ------------------------------------------------------

fact_user_risk_weekly = (
    fact_orders
    .groupby(["user_id", "week_start"])
    .agg(
        orders_count=("order_id", "count"),
        net_revenue=("net_amount", "sum"),
        refunds_count=("refund_flag", "sum"),
        refund_amount=("discount_amount", "sum"),  # adjust if refund_amount column exists
        coupon_orders_count=("coupon_id", lambda x: (x != "NO_COUPON").sum()),
        avg_discount_pct=("coupon_discount_pct", "mean"),
        cod_orders_count=("cod_flag", "sum"),
        payment_failures_count=("payment_fail_count_before_success", "sum"),
        risk_score_avg=("risk_score", "mean")
    )
    .reset_index()
)

# ------------------------------------------------------
# RTO Count (if available in shipments)
# ------------------------------------------------------

if "shipment_status" in fact_orders.columns:
    rto_counts = (
        fact_orders
        .groupby(["user_id", "week_start"])["shipment_status"]
        .apply(lambda x: (x == "rto").sum())
        .reset_index(name="rto_count")
    )

    fact_user_risk_weekly = fact_user_risk_weekly.merge(
        rto_counts,
        on=["user_id", "week_start"],
        how="left"
    )

else:
    fact_user_risk_weekly["rto_count"] = 0

print("Weekly user risk table created:", fact_user_risk_weekly.shape)

# ======================================================
# Step 9 — Save Required Outputs
# ======================================================

OUTPUT_PATH = os.path.join(BASE_DIR, "data")

os.makedirs(OUTPUT_PATH, exist_ok=True)

fact_orders.to_csv(os.path.join(OUTPUT_PATH, "fact_orders_enriched.csv"), index=False)
investigation_queue.to_csv(os.path.join(OUTPUT_PATH, "investigation_queue.csv"), index=False)
fact_user_risk_weekly.to_csv(os.path.join(OUTPUT_PATH, "fact_user_risk_weekly.csv"),index=False)

print("\nAll outputs saved successfully.")

# ======================================================
# Part D — Risk Scoring System
# ======================================================
fact_orders["risk_score"] = 0

## Add Weighted Signals

# Strong indicators
fact_orders["risk_score"] += (fact_orders["payment_fail_count_before_success"] > 2).astype(int) * 20
fact_orders["risk_score"] += (fact_orders["device_reuse_count"] > 3).astype(int) * 15
fact_orders["risk_score"] += fact_orders["high_discount_flag"] * 15
fact_orders["risk_score"] += (abs(fact_orders["order_value_zscore_by_category"]) > 2).astype(int) * 15

# Medium indicators
fact_orders["risk_score"] += fact_orders["new_user_flag"] * 10
fact_orders["risk_score"] += fact_orders["cod_flag"] * 10

# Mild indicators
fact_orders["risk_score"] += fact_orders["qty_outlier_flag"] * 5
fact_orders["risk_score"] += fact_orders["late_night_order_flag"] * 5
fact_orders["risk_score"] += fact_orders["multi_coupon_user_flag"] * 5
fact_orders["risk_score"] += (fact_orders["pincode_reuse_count"] > 5).astype(int) * 5

## Risk bands
# Percentile-based thresholds 
high_threshold = fact_orders["risk_score"].quantile(0.90)
medium_threshold = fact_orders["risk_score"].quantile(0.70)

def assign_risk_band(score):
    if score >= high_threshold:
        return "High"
    elif score >= medium_threshold:
        return "Medium"
    else:
        return "Low"

fact_orders["risk_band"] = fact_orders["risk_score"].apply(assign_risk_band)

## Top 3 Drivers
def get_top_drivers(row):
    drivers = []

    if row["payment_fail_count_before_success"] > 2:
        drivers.append("Multiple payment failures")

    if row["device_reuse_count"] > 3:
        drivers.append("Device reuse")

    if row["high_discount_flag"] == 1:
        drivers.append("High discount")

    if abs(row["order_value_zscore_by_category"]) > 2:
        drivers.append("Order value anomaly")

    if row["new_user_flag"] == 1:
        drivers.append("New user")

    if row["cod_flag"] == 1:
        drivers.append("COD")

    return ", ".join(drivers[:3])

fact_orders["top_3_drivers"] = fact_orders.apply(get_top_drivers, axis=1)

## Updates output
fact_orders.to_csv("data/fact_orders_enriched.csv", index=False)

