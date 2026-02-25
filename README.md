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


