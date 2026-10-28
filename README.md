# Fashion Retail Performance Analytics

A Streamlit dashboard for analyzing fashion retail performance across merchandising, supplier reliability, and inventory health. Built as a portfolio project demonstrating data analysis and business-oriented KPI reporting for an Increff-style retail operations use case.

## Business Objective

Retail businesses need visibility into product profitability, supplier delivery performance, and inventory exposure to make better merchandising and replenishment decisions.

This project brings these three areas together in an interactive dashboard.

## Dashboard Features

### 1. Executive Overview
- Recorded revenue and gross profit
- Revenue-weighted gross margin
- Units sold and average discount
- Provisional return rate
- Supplier delay rate and inventory value

### 2. Merchandising Performance
- Revenue and gross profit by category
- Category-level weighted gross margin
- Discount-band profitability analysis
- Brand performance scorecard
- Filters for category, brand, and sales date
- Automated business observations

### 3. Supplier Performance
- Supplier delay rate
- Average lateness among delayed orders
- Average lead time
- Quantity-weighted fulfillment rate
- Supplier-level scorecard and date filters

### 4. Inventory Health
- Inventory value and closing stock
- SKU-level inventory exposure
- Inventory health classifications
- Reported weeks of cover
- Snapshot-aware inventory comparisons

## Key Analytical Questions

- Which categories contribute the most recorded revenue and gross profit?
- How do gross margins vary across discount bands?
- Which suppliers have higher delivery delay rates?
- Which SKUs account for the largest share of recorded inventory value?
- Which inventory classifications warrant further investigation?

## Technology Stack

- Python
- Pandas
- Plotly
- Streamlit
- Git and GitHub

## Project Structure

```text
.
├── app.py
├── analysis.py
├── EDA.py
├── requirements.txt
├── README.md
└── cleaned_data/
    ├── products_clean.csv
    ├── sales_clean.csv
    ├── inventory_clean.csv
    └── purchase_orders_clean.csv
```

### Live Dashboard

```bash
https://fashion-retail-analytics-k4ucjdelpapppyscxvbb9nq.streamlit.app/
```
## Run Locally

### 1. Clone the repository

```bash
git clone https://github.com/AnAnYa-underWork/fashion-retail-analytics
cd fashion-retail-analytics
```

### 2. Create and activate a virtual environment

Windows:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Run the dashboard

```bash
python -m streamlit run app.py
```

Streamlit will provide a local URL in the terminal.

## Data Limitations

- The supplied dataset is synthetic and is intended for demonstrating an analytical workflow, not for claiming actual retailer performance.
- Sales revenue and gross profit are recorded values. Return adjustments have not been validated, so they should not be treated as confirmed net sales or net profit.
- Inventory coverage is limited to a small number of SKUs and should not be generalized to a complete retail assortment.
- Inventory health classifications come from the supplied dataset and have not been independently validated.
- All recorded inventory stockout flags are zero, so stockout performance cannot be compared meaningfully.
- Reported weeks of cover uses snapshot-level sales and may be volatile.
- Inventory metrics are calculated for the latest common snapshot date, excluding SKUs without a record on that date.

## Disclaimer

This is a portfolio analytics prototype built with supplied synthetic data. Findings are illustrative and should be validated against real operational data before making business decisions.
