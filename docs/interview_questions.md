# Interview Questions & Model Answers
## Based on: E-Commerce Sales and Customer Behavior Analysis

---

## SECTION 1 — PROJECT UNDERSTANDING

**Q1. Walk me through your project.**
> "I built an end-to-end e-commerce analytics portfolio project using the UCI Online
> Retail II dataset (~1 million transactions). I cleaned the data in Python, performed
> exploratory data analysis, segmented customers using RFM, answered business questions
> with SQL, and built a 3-page Power BI dashboard. The goal was to identify what drives
> revenue and who the most valuable customers are."

---

**Q2. Why did you choose the Online Retail II dataset?**
> "It closely mirrors real-world transactional data — it has customer IDs, timestamps,
> product codes, and prices, which allows me to demonstrate data cleaning, time-series
> analysis, customer segmentation, and geographic analysis in a single project — exactly
> what a BA does day-to-day."

---

**Q3. What was the most challenging part of the project?**
> "Data quality. About 25% of rows were missing CustomerID, there were negative quantities
> from cancelled orders (flagged by 'C' prefix on invoice numbers), and there were extreme
> outliers in order values. I had to make and document deliberate decisions — for example,
> I winsorised outliers instead of dropping them to preserve order volume."

---

## SECTION 2 — DATA CLEANING

**Q4. What steps did you take to clean the data?**
> "I followed a structured approach:
> 1. Removed duplicates
> 2. Dropped rows missing CustomerID (can't do customer analytics without it)
> 3. Filtered out cancelled orders (invoice starting with 'C')
> 4. Removed zero/negative quantities and prices
> 5. Fixed data types (datetime, int, float)
> 6. Winsorised total_sales outliers using IQR
> 7. Standardised text (title-case descriptions, stripped whitespace)"

---

**Q5. Why did you remove rows with missing CustomerID?**
> "The core objective was customer-level analysis — RFM, retention, CLV. Without a
> CustomerID, a transaction row can't be attributed to a customer. Imputation isn't
> appropriate here because CustomerID is an identity, not a measurable value."

---

## SECTION 3 — EDA & ANALYSIS

**Q6. What was your most important finding from EDA?**
> "Two stood out:
> 1. November and December drive disproportionately high revenue — a clear holiday spike.
>    This means inventory and marketing must be planned 6–8 weeks in advance.
> 2. UK accounts for ~85% of revenue. That's a concentration risk and also a growth
>    opportunity — small % gains in Germany or France have big absolute impact."

---

**Q7. How did you handle seasonality in the analysis?**
> "I plotted monthly and quarterly revenue trends, and used YoY comparison to separate
> seasonal patterns from actual growth. For the dashboard, I included a date slicer so
> stakeholders can compare any two periods side-by-side."

---

## SECTION 4 — RFM ANALYSIS

**Q8. Explain RFM in plain English as if to a non-technical stakeholder.**
> "RFM is a simple way to score every customer on three things:
> - Recency: how recently they bought (recent buyers are more likely to buy again)
> - Frequency: how often they buy (frequent buyers are loyal)
> - Monetary: how much they spend (high spenders are most valuable)
> We score each from 1–5, then combine the scores to place every customer into a
> group like 'Champions' (your best customers) or 'At Risk' (loyal customers going quiet).
> This tells your marketing team exactly who to talk to and what to offer them."

---

**Q9. How did you assign RFM scores?**
> "I used quintile-based scoring (pd.qcut with 5 bins). Each customer gets a 1–5 score
> per dimension based on where they fall in the distribution. For Recency, I reversed the
> scoring — fewer days since last purchase = higher score. For Frequency and Monetary,
> higher = better. I then concatenated the three scores to form a composite RFM code like
> '555' for Champions."

---

**Q10. Which segment would you prioritise for the business and why?**
> "At-Risk customers. They previously behaved like Loyal Customers — they buy frequently
> and spend well — but have gone quiet recently. Their average lifetime value is 3× the
> overall average. A targeted win-back email with a modest discount could recover a
> significant portion of their spend at a fraction of the cost of acquiring new customers."

---

## SECTION 5 — SQL

**Q11. Can you write a SQL query to find monthly revenue?**
```sql
SELECT
    year,
    month,
    ROUND(SUM(total_sales), 2) AS monthly_revenue,
    COUNT(DISTINCT invoice)    AS total_orders
FROM retail
GROUP BY year, month
ORDER BY year, month;
```

---

**Q12. How would you find customers who have not purchased in the last 90 days?**
```sql
SELECT
    customer_id,
    MAX(DATE(invoicedate)) AS last_purchase_date,
    JULIANDAY('now') - JULIANDAY(MAX(DATE(invoicedate))) AS days_since_purchase
FROM retail
GROUP BY customer_id
HAVING days_since_purchase > 90
ORDER BY days_since_purchase DESC;
```

---

**Q13. What are window functions and did you use them?**
> "Window functions perform calculations across a set of rows related to the current row
> without collapsing the result into a single row (unlike GROUP BY). I used them for:
> - RANK() OVER to find top revenue months
> - LAG() OVER to calculate quarter-over-quarter growth
> - SUM() OVER to compute percentage share of total revenue per country"

---

## SECTION 6 — POWER BI

**Q14. What DAX measures did you create?**
> "I created measures for:
> - Total Revenue = SUM(cleaned_retail[total_sales])
> - AOV = DIVIDE([Total Revenue], [Total Orders])
> - Repeat Customer Rate using CALCULATE + FILTER
> - Segment-specific counts using CALCULATE with a filter on the segment column"

---

**Q15. What is the difference between a Measure and a Calculated Column in Power BI?**
> "A Calculated Column is evaluated row-by-row at data refresh and stored in the model —
> useful for row-level values like 'total_sales = quantity × price'. A Measure is
> calculated at query time based on the current filter context — like 'Total Revenue'
> which changes when you click a country slicer. Measures are more memory-efficient for
> aggregations; calculated columns are better for row-level attributes."

---

## SECTION 7 — BUSINESS ACUMEN

**Q16. How would you present these findings to a non-technical executive?**
> "I would lead with the business outcome, not the method:
> 'Our top 8% of customers generate 38% of revenue. We risk losing 12% of our high-value
> customers who are showing early signs of disengagement. A targeted re-engagement
> campaign could recover £120K in revenue over the next quarter.'
> I would use the Power BI dashboard as a visual aid and avoid terms like 'quintile',
> 'IQR', or 'RFM score'."

---

**Q17. What would you do differently if this were a real company project?**
> "Several things:
> 1. Include qualitative data — customer surveys, support tickets — to understand *why*
>    customers churn, not just *that* they churn.
> 2. Track cohorts over time to measure true retention curves.
> 3. Build a CLV (Customer Lifetime Value) model to put a monetary figure on each segment.
> 4. Set up automated alerts in Power BI when KPIs breach thresholds."

---

**Q18. A stakeholder says 'your data shows UK is 85% of revenue — we should expand
       internationally'. How do you respond?**
> "I'd support the direction but add nuance. I'd look at international order volume and
> AOV trends — if Germany is growing 30% YoY even on a small base, that's a signal.
> But expansion also has costs — localisation, logistics, marketing. I'd recommend a
> market sizing analysis to compare the revenue opportunity against the entry cost before
> committing budget."

---

## QUICK-FIRE QUESTIONS

| Question | Short Answer |
|----------|-------------|
| What is AOV? | Average Order Value = Revenue ÷ Orders |
| What is churn? | % of customers who stop buying in a period |
| What is a KPI? | Key Performance Indicator — measurable business goal |
| Difference between mean and median? | Mean is average; median is middle value. Median is better for skewed data like revenue. |
| What is the 80/20 rule in business? | ~80% of revenue comes from ~20% of customers (Pareto principle) |
| Why use quintiles in RFM not fixed thresholds? | Quintiles adapt to the actual data distribution; fixed thresholds can become meaningless if data shifts |
| What is data granularity? | The level of detail in data — transaction-level is highest granularity; monthly summary is lower |
