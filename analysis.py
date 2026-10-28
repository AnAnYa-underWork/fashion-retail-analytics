import pandas as pd
from pathlib import Path

DATA_DIR = Path("cleaned_data")

products = pd.read_csv(DATA_DIR / "products_clean.csv")
sales = pd.read_csv(DATA_DIR / "sales_clean.csv")
purchase_orders = pd.read_csv(DATA_DIR / "purchase_orders_clean.csv")
inventory = pd.read_csv(DATA_DIR / "inventory_clean.csv")

print("Products:", products.shape)
print("Sales:", sales.shape)
print("Purchase orders:", purchase_orders.shape)

print("\nSales columns:")
print(sales.columns.tolist())

print("\nSales preview:")
print(sales.head())


# 1. Check the sales data before analysis

print("\n--- SALES DATA QUALITY ---")
print("Missing values:")
print(sales.isnull().sum()[sales.isnull().sum() > 0])

print("\nReturned vs non-returned records:")
print(sales["is_returned"].value_counts(dropna=False))

print("\nSales date range:")
print(sales["sale_date"].min(), "to", sales["sale_date"].max())

print("\n--- OVERALL SALES METRICS ---")
print("Total recorded revenue:", round(sales["revenue"].sum(), 2))
print("Total recorded gross profit:", round(sales["gross_profit"].sum(), 2))
print("Total units:", sales["quantity"].sum())
print("Average gross margin (%):",
      round(sales["gross_margin_pct"].mean(), 2))

# 2. Category performance

category_performance = (
    sales.groupby("category")
    .agg(
        recorded_revenue=("revenue", "sum"),
        gross_profit=("gross_profit", "sum"),
        units_sold=("quantity", "sum"),
        transactions=("sale_id", "count"),
        avg_margin_pct=("gross_margin_pct", "mean")
    )
    .sort_values("recorded_revenue", ascending=False)
)

print("\n--- CATEGORY PERFORMANCE ---")
print(category_performance.round(2).to_string())

# 3. Brand performance

brand_performance = (
    sales.groupby("brand")
    .agg(
        recorded_revenue=("revenue", "sum"),
        gross_profit=("gross_profit", "sum"),
        units_sold=("quantity", "sum"),
        avg_margin_pct=("gross_margin_pct", "mean")
    )
    .sort_values("recorded_revenue", ascending=False)
)

print("\n--- TOP 10 BRANDS BY REVENUE ---")
print(brand_performance.head(10).round(2).to_string())


# 4. Discount analysis

sales["discount_band"] = pd.cut(
    sales["discount_pct"],
    bins=[-0.01, 10, 20, 30, 40, 100],
    labels=["0-10%", "10-20%", "20-30%", "30-40%", "40%+"],
    include_lowest=True
)

discount_analysis = (
    sales.groupby("discount_band", observed=False)
    .agg(
        transactions=("sale_id", "count"),
        recorded_revenue=("revenue", "sum"),
        gross_profit=("gross_profit", "sum"),
        avg_margin_pct=("gross_margin_pct", "mean"),
        avg_discount_pct=("discount_pct", "mean")
    )
)

print("\n--- DISCOUNT ANALYSIS ---")
print(discount_analysis.round(2).to_string())

# 5. Returns analysis

print("\n--- RETURN ANALYSIS ---")

return_analysis = (
    sales.groupby("is_returned", dropna=False)
    .agg(
        transactions=("sale_id", "count"),
        recorded_revenue=("revenue", "sum"),
        gross_profit=("gross_profit", "sum"),
        units=("quantity", "sum")
    )
)

print(return_analysis.round(2).to_string())

print(
    "\nReturned transaction share (%):",
    round(sales["is_returned"].eq(1).mean() * 100, 2)
)


# 6. Supplier performance analysis

print("\n--- PURCHASE ORDER COLUMNS ---")
print(purchase_orders.columns.tolist())

# Convert delivery dates to datetime
for col in ["po_date", "expected_delivery", "actual_delivery"]:
    if col in purchase_orders.columns:
        purchase_orders[col] = pd.to_datetime(
            purchase_orders[col], errors="coerce"
        )

print("\n--- DELIVERY DATE VALIDATION ---")
for col in ["po_date", "expected_delivery", "actual_delivery"]:
    if col in purchase_orders.columns:
        print(col, "missing/unparsed:", purchase_orders[col].isna().sum())

print("\n--- SUPPLIER PERFORMANCE ---")

# Adjust these names if your printed column list differs
purchase_orders["delay_days"] = (
    purchase_orders["actual_delivery"]
    - purchase_orders["expected_delivery"]
).dt.days

purchase_orders["is_delayed"] = (
    purchase_orders["delay_days"] > 0
)

supplier_performance = (
    purchase_orders.groupby("supplier")
    .agg(
        purchase_orders=("po_id", "count"),
        delayed_orders=("is_delayed", "sum"),
        avg_delay_days=("delay_days", "mean")
    )
)

supplier_performance["delay_rate_pct"] = (
    supplier_performance["delayed_orders"]
    / supplier_performance["purchase_orders"] * 100
)

print(supplier_performance.sort_values(
    "delay_rate_pct", ascending=False
).round(2).to_string())


# 7. Validate delay flags and build the final supplier scorecard

print("\n--- DELAY FLAG VALIDATION ---")

calculated_delay_flag = (
    purchase_orders["actual_delivery"]
    > purchase_orders["expected_delivery"]
)

print(
    "Existing is_delayed vs calculated mismatch:",
    (
        purchase_orders["is_delayed"].astype(int)
        != calculated_delay_flag.astype(int)
    ).sum()
)

# Calculate delay only for orders delivered late
purchase_orders["late_days_only"] = (
    purchase_orders["actual_delivery"]
    - purchase_orders["expected_delivery"]
).dt.days.where(calculated_delay_flag)

supplier_scorecard = (
    purchase_orders.groupby("supplier")
    .agg(
        orders=("po_id", "count"),
        delayed_orders=("is_delayed", "sum"),
        delay_rate_pct=("is_delayed", "mean"),
        avg_lead_time_days=("lead_time_days", "mean"),
        avg_late_days=("late_days_only", "mean"),
        avg_fulfillment_pct=("fulfillment_rate", "mean"),
        total_po_value=("po_value", "sum")
    )
)

supplier_scorecard["delay_rate_pct"] *= 100

print("\n--- FINAL SUPPLIER SCORECARD ---")
print(
    supplier_scorecard
    .sort_values("delay_rate_pct", ascending=False)
    .round(2)
    .to_string()
)

# 8. Inventory analysis

print("\n--- INVENTORY COLUMNS ---")
print(inventory.columns.tolist())

print("\n--- INVENTORY HEALTH DISTRIBUTION ---")
print(inventory["inventory_health"].value_counts(dropna=False))


# Latest available snapshot for each SKU
inventory["snapshot_date"] = pd.to_datetime(
    inventory["snapshot_date"], format="%Y-%m-%d", errors="coerce"
)

latest_inventory = (
    inventory.sort_values("snapshot_date")
    .groupby("sku_id", as_index=False)
    .tail(1)
    .copy()
)

print("\n--- LATEST INVENTORY SNAPSHOT BY SKU ---")
print("SKUs:", latest_inventory["sku_id"].nunique())
print("Snapshot dates:", latest_inventory["snapshot_date"].nunique())

print("\n--- INVENTORY DATA PREVIEW ---")
print(latest_inventory.head().to_string(index=False))

print("\n--- LATEST INVENTORY BY SKU ---")

inventory_summary = latest_inventory[
    [
        "sku_id",
        "brand",
        "category",
        "snapshot_date",
        "closing_stock",
        "reorder_point",
        "weeks_of_cover",
        "inventory_health",
        "inventory_value"
    ]
].sort_values("inventory_value", ascending=False)

print(inventory_summary.round(2).to_string(index=False))

print("\n--- TOTAL INVENTORY VALUE ---")
print(round(latest_inventory["inventory_value"].sum(), 2))


print("\n--- SNAPSHOT DATE COVERAGE BY SKU ---")

print(
    inventory.groupby("sku_id")
    .agg(
        snapshot_count=("snapshot_date", "count"),
        first_snapshot=("snapshot_date", "min"),
        latest_snapshot=("snapshot_date", "max")
    )
    .to_string()
)

print("\n--- LATEST COMMON SNAPSHOT DATE ---")

latest_common_date = inventory["snapshot_date"].max()
print("Latest date in dataset:", latest_common_date)

common_date_inventory = inventory[
    inventory["snapshot_date"] == latest_common_date
].copy()

print("SKUs available on this date:", common_date_inventory["sku_id"].nunique())
print("Inventory value on this date:",
      round(common_date_inventory["inventory_value"].sum(), 2))

print("\n--- STOCKOUT VALIDATION ---")
print(inventory["stockout_flag"].value_counts(dropna=False))

