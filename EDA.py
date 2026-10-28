
from pathlib import Path
import pandas as pd
import numpy as np

# ============================================================
# 1. CONFIGURATION
# ============================================================

DATA_DIR = Path(__file__).resolve().parent

FILES = {
    "products": "products.csv",
    "sales": "sales_transactions.csv",
    "inventory": "inventory.csv",
    "purchase_orders": "purchase_orders.csv",
    "trend_signals": "trend_signals.csv",
    "social_signals": "social_signals.csv",
    "trend_sku_mapping": "trend_sku_mapping.csv",
}

# IDs must remain strings, even if they look numeric.
STRING_COLUMNS = {
    "products": ["sku_id"],
    "sales": ["sale_id", "sku_id"],
    "inventory": ["inventory_id", "sku_id"],
    "purchase_orders": ["po_id", "sku_id"],
    "trend_signals": ["trend_id"],
    "social_signals": ["signal_id", "trend_id"],
    "trend_sku_mapping": ["mapping_id", "trend_id", "sku_id"],
}

DATE_FORMATS = {
    "sales": {
        "sale_date": "%d-%m-%Y",
    },
    "inventory": {
        "snapshot_date": "%d-%m-%Y",
    },
    "purchase_orders": {
        "po_date": "%Y-%m-%d",
        "expected_delivery": "%Y-%m-%d",
        "actual_delivery": "%Y-%m-%d",
    },
    "trend_signals": {
        "week_start_date": "%Y-%m-%d",
    },
    "social_signals": {
        "week_start_date": "%Y-%m-%d",
    },
}

# Keep the raw and cleaned versions separate.
raw_tables = {}
tables = {}


# ============================================================
# 2. LOAD CSV FILES AND INVESTIGATE BLANK ROWS
# ============================================================

print("\n" + "=" * 75)
print("STEP 1: RAW CSV INSPECTION AND LOADING")
print("=" * 75)

for name, filename in FILES.items():
    path = DATA_DIR / filename

    if not path.exists():
        raise FileNotFoundError(
            f"Cannot find {filename}. "
            f"Expected location: {path}"
        )

    # Inspect the physical file before pandas reads it.
    with open(path, "r", encoding="utf-8-sig", newline="") as file:
        physical_lines = file.readlines()

    empty_physical_lines = sum(
        not line.strip() for line in physical_lines
    )

    # Retain blank lines initially so their effect is measurable.
    raw_df = pd.read_csv(
        path,
        dtype={
            col: "string"
            for col in STRING_COLUMNS.get(name, [])
        },
        skip_blank_lines=False,
        encoding="utf-8-sig",
    )

    # Convert whitespace-only cells to missing values.
    # This does not convert legitimate zeros into missing values.
    raw_df = raw_df.replace(r"^\s*$", pd.NA, regex=True)

    raw_tables[name] = raw_df.copy()

    rows_loaded = len(raw_df)
    fully_blank_records = int(raw_df.isna().all(axis=1).sum())

    # Remove only rows in which every column is blank.
    clean_df = raw_df.dropna(how="all").copy()

    # Explicit date parsing.
    for col, date_format in DATE_FORMATS.get(name, {}).items():
        if col in clean_df.columns:
            clean_df[col] = pd.to_datetime(
                clean_df[col],
                format=date_format,
                errors="coerce",
            )

    tables[name] = clean_df

    print(f"\nFile: {filename}")
    print(f"Physical lines in file: {len(physical_lines)}")
    print(f"Completely empty physical lines: {empty_physical_lines}")
    print(f"Rows loaded by pandas: {rows_loaded}")
    print(f"Fully blank records removed: {fully_blank_records}")
    print(f"Rows remaining: {len(clean_df)}")

# ============================================================
# 3. POST-CLEANING DATA-QUALITY AUDIT
# ============================================================

print("\n" + "=" * 75)
print("STEP 2: POST-CLEANING DATA-QUALITY AUDIT")
print("=" * 75)

for name, df in tables.items():
    print(f"\n--- {name.upper()} ---")
    print(f"Shape: {df.shape}")
    print(f"Duplicate rows: {df.duplicated().sum()}")
    print(f"Fully blank rows remaining: {df.isna().all(axis=1).sum()}")
    print(f"Total missing cells: {df.isna().sum().sum()}")

    missing_by_column = df.isna().sum()
    missing_by_column = missing_by_column[missing_by_column > 0]

    if not missing_by_column.empty:
        print("Columns with missing values:")
        print(missing_by_column.to_string())
    else:
        print("No missing cells.")

    # Check date parsing and valid ranges.
    for col in DATE_FORMATS.get(name, {}):
        if col in df.columns:
            invalid_count = int(df[col].isna().sum())
            valid_dates = df[col].dropna()

            print(f"{col}: missing/invalid dates = {invalid_count}")

            if not valid_dates.empty:
                print(
                    f"  Date range: {valid_dates.min().date()} "
                    f"to {valid_dates.max().date()}"
                )

    # Verify ID column types.
    for col in STRING_COLUMNS.get(name, []):
        if col in df.columns:
            print(f"{col} dtype: {df[col].dtype}")


# ============================================================
# 4. CHECK IDENTIFIER AND JOIN QUALITY
# ============================================================

print("\n" + "=" * 75)
print("STEP 3: SKU AND RELATIONSHIP CHECKS")
print("=" * 75)

products = tables["products"]
sales = tables["sales"]
inventory = tables["inventory"]
purchase_orders = tables["purchase_orders"]
trend_signals = tables["trend_signals"]
social_signals = tables["social_signals"]
trend_sku_mapping = tables["trend_sku_mapping"]

if "sku_id" in products.columns:
    product_skus = set(products["sku_id"].dropna())

    for name in ["sales", "inventory", "purchase_orders",
                 "trend_sku_mapping"]:
        df = tables[name]

        if "sku_id" in df.columns:
            referenced_skus = set(df["sku_id"].dropna())
            unmatched = referenced_skus - product_skus

            print(
                f"{name}: unique SKUs not found in products = "
                f"{len(unmatched)}"
            )

            if unmatched:
                print("  Examples:", list(unmatched)[:10])

if "trend_id" in trend_signals.columns:
    known_trends = set(trend_signals["trend_id"].dropna())

    for name in ["social_signals", "trend_sku_mapping"]:
        df = tables[name]

        if "trend_id" in df.columns:
            referenced_trends = set(df["trend_id"].dropna())
            unmatched = referenced_trends - known_trends

            print(
                f"{name}: unique trend IDs not found in trend_signals = "
                f"{len(unmatched)}"
            )


# ============================================================
# 5. VALIDATE SALES CALCULATIONS
# ============================================================

print("\n" + "=" * 75)
print("STEP 4: SALES CALCULATION VALIDATION")
print("=" * 75)

sales_required = [
    "quantity", "selling_price", "revenue",
    "cogs", "gross_profit", "gross_margin_pct"
]

if all(col in sales.columns for col in sales_required):
    s = sales.copy()

    # Convert calculation columns to numeric where possible.
    for col in sales_required:
        s[col] = pd.to_numeric(s[col], errors="coerce")

    expected_revenue = s["selling_price"] * s["quantity"]
    expected_profit = s["revenue"] - s["cogs"]

    # Compare against the recorded revenue and profit.
    revenue_valid = s["revenue"].notna() & expected_revenue.notna()
    profit_valid = s["gross_profit"].notna() & expected_profit.notna()

    revenue_mismatches = (
        (s.loc[revenue_valid, "revenue"]
         - expected_revenue.loc[revenue_valid]).abs() > 0.02
    ).sum()

    profit_mismatches = (
        (s.loc[profit_valid, "gross_profit"]
         - expected_profit.loc[profit_valid]).abs() > 0.02
    ).sum()

    # Avoid division by zero.
    margin_valid = (
        s["revenue"].notna()
        & s["gross_profit"].notna()
        & s["gross_margin_pct"].notna()
        & s["revenue"].ne(0)
    )

    expected_margin = (
        s.loc[margin_valid, "gross_profit"]
        / s.loc[margin_valid, "revenue"] * 100
    )

    margin_mismatches = (
        (s.loc[margin_valid, "gross_margin_pct"]
         - expected_margin).abs() > 0.1
    ).sum()

    print("Valid revenue comparisons:", int(revenue_valid.sum()))
    print("Revenue mismatches:", int(revenue_mismatches))
    print("Valid profit comparisons:", int(profit_valid.sum()))
    print("Gross profit mismatches:", int(profit_mismatches))
    print("Valid margin comparisons:", int(margin_valid.sum()))
    print("Gross margin mismatches:", int(margin_mismatches))
else:
    print("Sales validation skipped: required columns are missing.")


# ============================================================
# 6. VALIDATE INVENTORY STOCK EQUATION
# ============================================================

print("\n" + "=" * 75)
print("STEP 5: INVENTORY STOCK VALIDATION")
print("=" * 75)

stock_columns = [
    "opening_stock", "units_received",
    "units_sold", "closing_stock"
]

if all(col in inventory.columns for col in stock_columns):
    inv = inventory.copy()

    for col in stock_columns:
        inv[col] = pd.to_numeric(inv[col], errors="coerce")

    expected_closing = (
        inv["opening_stock"]
        + inv["units_received"]
        - inv["units_sold"]
    )

    comparable = (
        inv["closing_stock"].notna()
        & expected_closing.notna()
    )

    difference = (
        inv.loc[comparable, "closing_stock"]
        - expected_closing.loc[comparable]
    )

    mismatches = difference.abs() > 0.01

    print("Records checked:", int(comparable.sum()))
    print("Stock equation mismatches:", int(mismatches.sum()))

    if mismatches.any():
        print("\nExample mismatches:")
        print(
            inv.loc[comparable].loc[
                mismatches,
                ["sku_id", "snapshot_date"] + stock_columns
            ].head(10).to_string(index=False)
        )
else:
    print("Inventory stock validation skipped: required columns missing.")


# ============================================================
# 7. INVESTIGATE WEEKS OF COVER
# ============================================================

print("\n" + "=" * 75)
print("STEP 6: WEEKS-OF-COVER INVESTIGATION")
print("=" * 75)

if "weeks_of_cover" in inventory.columns:
    inv = inventory.copy()

    numeric_cols = [
        "opening_stock", "units_sold", "units_received",
        "closing_stock", "weeks_of_cover",
        "lead_time_days", "inventory_value",
        "stockout_flag"
    ]

    for col in numeric_cols:
        if col in inv.columns:
            inv[col] = pd.to_numeric(inv[col], errors="coerce")

    print("\nWeeks-of-cover distribution:")
    print(inv["weeks_of_cover"].describe().to_string())

    if "inventory_health" in inv.columns:
        print("\nInventory health counts:")
        print(
            inv["inventory_health"]
            .value_counts(dropna=False)
            .to_string()
        )

    if "stockout_flag" in inv.columns:
        print("\nStockout flag counts:")
        print(
            inv["stockout_flag"]
            .value_counts(dropna=False)
            .to_string()
        )

    # Diagnostic only: assumes units_sold represents one week of demand.
    # Do not treat this as a validated cover KPI until the period is verified.
    if {"closing_stock", "units_sold"}.issubset(inv.columns):
        inv["diagnostic_cover"] = (
            inv["closing_stock"]
            / inv["units_sold"].where(inv["units_sold"] > 0)
        )

        print("\nReported vs diagnostic cover (first 20 records):")
        print(
            inv[
                ["sku_id", "snapshot_date", "closing_stock",
                 "units_sold", "weeks_of_cover", "diagnostic_cover"]
            ].head(20).to_string(index=False)
        )

        print("\nHighest reported weeks of cover:")
        print(
            inv.nlargest(10, "weeks_of_cover")[
                ["sku_id", "snapshot_date", "closing_stock",
                 "units_sold", "weeks_of_cover", "diagnostic_cover"]
            ].to_string(index=False)
        )

    # Check whether the same SKU has multiple weekly snapshots.
    if {"sku_id", "snapshot_date"}.issubset(inv.columns):
        print(
            "\nRows with missing SKU or snapshot date:",
            int(inv[["sku_id", "snapshot_date"]].isna().any(axis=1).sum())
        )

        duplicate_sku_dates = inv.duplicated(
            subset=["sku_id", "snapshot_date"],
            keep=False
        )

        print(
            "Duplicate SKU-date records:",
            int(duplicate_sku_dates.sum())
        )

        inv_sorted = inv.dropna(
            subset=["sku_id", "snapshot_date"]
        ).sort_values(["sku_id", "snapshot_date"])

        print(
            "Unique SKUs in inventory:",
            inv["sku_id"].nunique()
        )
        print(
            "Unique snapshot dates:",
            inv["snapshot_date"].nunique()
        )

else:
    print("weeks_of_cover column not found.")


# ============================================================
# 8. PURCHASE ORDER / SUPPLIER CHECKS
# ============================================================

print("\n" + "=" * 75)
print("STEP 7: SUPPLIER PERFORMANCE")
print("=" * 75)

po = purchase_orders.copy()

for col in [
    "lead_time_days", "delay_days",
    "qty_ordered", "qty_received",
    "fulfillment_rate", "po_value"
]:
    if col in po.columns:
        po[col] = pd.to_numeric(po[col], errors="coerce")

if "is_delayed" in po.columns:
    print("\nDelayed vs not delayed:")
    print(po["is_delayed"].value_counts(dropna=False).to_string())

if "supplier" in po.columns:
    supplier_summary = po.groupby("supplier", dropna=False).agg(
        purchase_orders=("po_id", "count"),
        avg_lead_time_days=("lead_time_days", "mean"),
        avg_delay_days=("delay_days", "mean"),
        avg_fulfillment_rate=("fulfillment_rate", "mean"),
        total_po_value=("po_value", "sum"),
    ).sort_values("avg_delay_days", ascending=False)

    print("\nSupplier summary:")
    print(supplier_summary.round(2).to_string())


# ============================================================
# 9. SAVE CLEANED COPIES WITHOUT MODIFYING ORIGINAL CSVs
# ============================================================

print("\n" + "=" * 75)
print("STEP 8: SAVE CLEANED DATA")
print("=" * 75)

OUTPUT_DIR = DATA_DIR / "cleaned_data"
OUTPUT_DIR.mkdir(exist_ok=True)

for name, df in tables.items():
    output_path = OUTPUT_DIR / f"{name}_clean.csv"
    df.to_csv(output_path, index=False)
    print(f"Saved: {output_path.name} ({len(df)} rows)")

print("\nEDA audit completed.")
print("Original CSV files were not modified.")
