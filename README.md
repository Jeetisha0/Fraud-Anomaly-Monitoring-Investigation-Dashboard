# Fraud-Anomaly-Monitoring-Investigation-Dashboard
# ## Part A — Problem Framing

##  Business Objective

The primary objective of this project is to reduce fraud-related financial losses while minimizing false positives that negatively impact genuine customers. The system aims to proactively identify suspicious transactions using explainable risk signals, enabling faster investigation and operational decision-making. By balancing fraud detection accuracy with customer experience, the solution supports sustainable risk management and business growth.

##  North Star Metric

### Selected Metric: **Monthly Fraud Loss Prevented (₹)**

### Justification:
 This metric directly reflects business impact by quantifying how much financial loss is avoided through early detection and intervention. Unlike pure detection rates, measuring loss prevented ensures that the system prioritizes high-impact fraud cases rather than simply increasing flagged orders. It also aligns closely with executive decision-making and ROI evaluation.


##  Key Performance Indicators (KPIs)

1. Refund Rate (%): Percentage of orders resulting in refunds.

2. Refund Amount (₹): Total monetary value lost through refunds.

3. Return-to-Origin (RTO) Rate for COD Orders (%): Measures failed deliveries and potential abuse.

4. Coupon Usage Rate (%): Percentage of orders using promotional discounts.

5. Average Discount Percentage (%): Identifies excessive discount patterns linked to fraud.

6. Payment Failure Rate per Session/Order: Indicates potential card testing or suspicious payment behaviour.

7. Suspicious Orders Rate (%): Percentage of orders flagged based on fraud risk score threshold.

8. Investigation Precision Proxy: Ratio of flagged orders that later result in refund or RTO.

9. New User Fraud Rate (%): Fraud occurrence among newly created accounts.

10. Device Reuse Frequency: Multiple accounts/orders from same device signals potential fraud rings.

11. Late-Night Order Ratio (%): Orders placed during high-risk time windows.

12. Average Order Value (AOV) Trends: Detect abnormal purchase patterns.


##  Guardrail Metric: **Overall Conversion Rate / Gross Revenue Trend**

Fraud detection must not negatively impact genuine customers or reduce business growth. Monitoring conversion or revenue ensures risk controls do not create excessive friction.


##  Stakeholder Questions

1. Which coupons are most frequently associated with refunds or suspicious activity?
2. Which payment methods show the highest failure or fraud risk?
3. Are new users contributing disproportionately to fraud losses?
4. Which regions or pincodes show abnormal RTO patterns?
5. What behavioural signals best predict fraudulent outcomes?
6. How many flagged orders actually result in financial loss?
7. What operational controls can reduce fraud without impacting legitimate customers?


# Definitions

### Fraud / Anomaly

Fraud refers to suspicious transactions or behaviors that intentionally exploit the system for financial gain, such as fake orders, coupon abuse, or payment manipulation.
An anomaly refers to unusual patterns in transaction behavior that deviate from normal user activity and may indicate potential fraud.

### Loss Proxy

Actual fraud loss is not directly labeled in the dataset. Therefore, refund amounts and RTO-related orders are used as a proxy for financial fraud loss. These values approximate the monetary impact of suspicious transactions.

### Risk Score

The risk score is a numerical value assigned to each order based on multiple behavioral signals such as:

* high discount usage
* new user placing orders
* late night orders
* multiple payment failures
* device reuse
* quantity anomalies

Higher scores indicate a higher likelihood that the order may be fraudulent.

Orders are categorized into risk bands:

* **High Risk** – requires manual investigation
* **Medium Risk** – requires monitoring
* **Low Risk** – normal transaction behavior

# How to Run the ETL Pipeline

To run the ETL pipeline and generate the curated datasets:

### Step 1 — Clone the Repository
git clone <repository_url>
cd Fraud-Anomaly-Monitoring-Investigation-Dashboard

### Step 2 — Install Required Python Libraries
pip install pandas numpy


### Step 3 — Run the ETL Pipeline
python etl/etl_pipeline.py
(This script loads the raw datasets, performs data cleaning and joins, generates fraud signals, and produces the curated analytical tables.)


# Curated Outputs Generated

Running the ETL pipeline produces the following datasets inside the **/data** folder:

### fact_orders_enriched.csv
Order-level dataset containing transaction details, engineered fraud signals, and calculated risk scores.

### fact_user_risk_weekly.csv
Weekly aggregated dataset summarizing user behavior, including order count, refunds, coupon usage, and average risk score.

### investigation_queue.csv
Operational dataset listing orders ranked by fraud risk along with recommended actions and evidence fields for investigation.


# Dashboard Tool Used
The analytical dashboard was built using **Power BI**.

### How to Open the Dashboard
1. Open **Power BI Desktop**
2. Navigate to the **/dashboard** folder
3. Open the file:
fraud_monitoring_dashboard.pbix

If the dataset needs to be refreshed:
Home → Refresh
(This will reload the latest curated datasets generated by the ETL pipeline.)
