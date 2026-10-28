from pathlib import Path
from html import escape
import pandas as pd
import plotly.express as px
import streamlit as st

# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------
st.set_page_config(
    page_title="Retail Performance Analytics",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded",
)

DATA_DIR = Path(__file__).parent / "cleaned_data"

# --------------------------------------------------
# REFINED SAAS DESIGN SYSTEM
# --------------------------------------------------
NAVY = "#142B4A"
RED = "#D9272E"
BLUE = "#5379A5"
LIGHT_BLUE = "#9BB2CC"
TEXT = "#25364B"
MUTED = "#718096"
BG = "#F5F7FA"
BORDER = "#E5EAF1"
WHITE = "#FFFFFF"
GRID = "#E9EDF3"

st.markdown(
    """
    <style>
    /* App canvas */
    .stApp {
        background: #F5F7FA;
        color: #25364B;
    }

    .block-container {
        max-width: 1560px;
        padding: 1.8rem 2.3rem 3rem 2.3rem;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: #142B4A;
        border-right: 1px solid #253D59;
    }

    [data-testid="stSidebar"] > div:first-child {
        padding: 1.5rem 1rem 1rem;
    }

    [data-testid="stSidebar"] * {
        color: #FFFFFF;
    }

    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
        color: #C1CDDB;
        font-size: 0.84rem;
        line-height: 1.5;
    }

    [data-testid="stSidebar"] hr {
        border-color: #344A64;
        margin: 1.25rem 0;
    }

    /* Sidebar navigation */
    [data-testid="stSidebar"] [role="radiogroup"] {
        gap: 0.35rem;
    }

    [data-testid="stSidebar"] [role="radiogroup"] label {
        padding: 0.55rem 0.7rem;
        border-radius: 8px;
        transition: background 0.15s ease;
    }

    [data-testid="stSidebar"] [role="radiogroup"] label:hover {
        background: #203B5C;
    }

    /* Typography */
    h1 {
        color: #142B4A !important;
        font-size: 2.05rem !important;
        font-weight: 750 !important;
        letter-spacing: -0.8px;
        line-height: 1.2 !important;
    }

    h2 {
        color: #142B4A !important;
        font-size: 1.35rem !important;
        font-weight: 700 !important;
        letter-spacing: -0.35px;
    }

    h3 {
        color: #142B4A !important;
        font-size: 1.02rem !important;
        font-weight: 650 !important;
    }

    p, li {
        line-height: 1.6;
    }

    
    /* KPI card labels */
    div[data-testid="stMetricLabel"],
    div[data-testid="stMetricLabel"] p,
    div[data-testid="stMetricLabel"] label {
        color: #718096 !important;
        font-size: 0.8rem !important;
        font-weight: 600 !important;
        opacity: 1 !important;
    }


    /* Filters */
    div[data-baseweb="select"] > div,
    div[data-baseweb="input"] > div {
        background: #FFFFFF;
        border-color: #DCE3EC;
        border-radius: 8px;
    }

    /* Tables */
    div[data-testid="stDataFrame"] {
        background: #FFFFFF;
        border: 1px solid #E5EAF1;
        border-radius: 10px;
        overflow: hidden;
    }

    /* Tabs, alerts, buttons */
    .stTabs [data-baseweb="tab-list"] {
        gap: 1.1rem;
        border-bottom: 1px solid #E5EAF1;
    }

    .stTabs [data-baseweb="tab"] {
        padding: 0.7rem 0.15rem;
        font-weight: 600;
    }

    div[data-testid="stAlert"] {
        border-radius: 10px;
    }

    .stButton > button {
        border-radius: 8px;
        font-weight: 600;
        border: 1px solid #DCE3EC;
        transition: all 0.15s ease;
    }

    hr {
        border-color: #E5EAF1 !important;
        margin: 1.5rem 0;
    }

    /* Reusable page components */
    .page-eyebrow {
        color: #D9272E;
        font-size: 0.72rem;
        font-weight: 750;
        letter-spacing: 1.3px;
        text-transform: uppercase;
        margin-bottom: 0.35rem;
    }

    .page-subtitle {
        color: #718096;
        font-size: 0.93rem;
        margin-top: -0.45rem;
        margin-bottom: 1.35rem;
    }

    .section-caption {
        color: #718096;
        font-size: 0.83rem;
        margin-top: -0.5rem;
        margin-bottom: 0.9rem;
    }

    .insight-panel {
        background: #FFFFFF;
        border: 1px solid #E5EAF1;
        border-left: 4px solid #D9272E;
        border-radius: 10px;
        padding: 1rem 1.1rem;
        margin: 0.35rem 0 1rem;
    }

    .insight-label {
        color: #D9272E;
        font-size: 0.7rem;
        font-weight: 750;
        letter-spacing: 0.9px;
        text-transform: uppercase;
        margin-bottom: 0.35rem;
    }

    .insight-body {
        color: #25364B;
        font-size: 0.9rem;
        line-height: 1.6;
    }

    .dashboard-footer {
        color: #8793A4;
        font-size: 0.76rem;
        border-top: 1px solid #E5EAF1;
        padding-top: 1rem;
        margin-top: 2.5rem;
    }

    </style>
    """,
    unsafe_allow_html=True,
)

# --------------------------------------------------
# DATA LOADING
# --------------------------------------------------
@st.cache_data
def load_data():
    required_files = {
        "products": "products_clean.csv",
        "sales": "sales_clean.csv",
        "inventory": "inventory_clean.csv",
        "purchase_orders": "purchase_orders_clean.csv",
    }

    data = {}

    for name, filename in required_files.items():
        path = DATA_DIR / filename

        if not path.exists():
            raise FileNotFoundError(
                f"Missing file: {path}"
            )

        data[name] = pd.read_csv(path)

    return data


try:
    data = load_data()
except (FileNotFoundError, pd.errors.ParserError) as error:
    st.error(f"Could not load the required data: {error}")
    st.stop()

sales = data["sales"]
inventory = data["inventory"]
purchase_orders = data["purchase_orders"]
products = data["products"]


# --------------------------------------------------
# CHART THEME
# --------------------------------------------------

NAVY = "#142B4A"
RED = "#D9272E"
BLUE = "#5379A5"
LIGHT_BLUE = "#9BB2CC"
GREY = "#64748B"
GRID = "#E2E8F0"



def style_chart(fig, height=360):
    fig.update_layout(
        height=height,
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        font=dict(
            family="Arial, sans-serif",
            color="#25364B",
            size=12,
        ),
        margin=dict(l=12, r=18, t=35, b=12),
        title=dict(
            font=dict(size=15, color="#142B4A"),
            x=0,
            xanchor="left",
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=10, color="#64748B"),
        ),
        hoverlabel=dict(
            bgcolor="#142B4A",
            font=dict(color="#FFFFFF", size=12),
            bordercolor="#142B4A",
        ),
        xaxis=dict(
            showgrid=False,
            showline=True,
            linecolor="#E5EAF1",
            tickfont=dict(color="#64748B", size=10),
            automargin=True,
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor="#E9EDF3",
            gridwidth=1,
            zeroline=False,
            showline=False,
            tickfont=dict(color="#64748B", size=10),
            automargin=True,
        ),
    )

    return fig


def render_insight(title, message):
    """Render a concise, data-driven business insight panel."""
    safe_title = escape(str(title))
    safe_message = escape(str(message))
    st.markdown(
        f"""
        <div class="insight-panel">
            <div class="insight-label">{safe_title}</div>
            <div class="insight-body">{safe_message}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# --------------------------------------------------
# KPI CALCULATIONS
# --------------------------------------------------

# Sales metrics
total_revenue = sales["revenue"].sum()
total_gross_profit = sales["gross_profit"].sum()
total_units = sales["quantity"].sum()

# Revenue-weighted gross margin
weighted_margin = (
    total_gross_profit / total_revenue * 100
    if total_revenue else 0
)

# Transaction-weighted average discount
avg_discount = sales["discount_pct"].mean()

# Provisional return rate
return_rate = sales["is_returned"].eq(1).mean() * 100

# Supplier metrics
total_orders = len(purchase_orders)

supplier_delay_rate = (
    purchase_orders["is_delayed"].mean() * 100
    if total_orders else 0
)

# Inventory value on the latest common snapshot date
inventory["snapshot_date"] = pd.to_datetime(
    inventory["snapshot_date"],
    format="%Y-%m-%d",
    errors="coerce",
)

latest_snapshot = inventory["snapshot_date"].max()

latest_inventory = inventory[
    inventory["snapshot_date"] == latest_snapshot
].copy()

inventory_value = latest_inventory["inventory_value"].sum()
inventory_sku_count = latest_inventory["sku_id"].nunique()

# --------------------------------------------------
# SIDEBAR NAVIGATION
# --------------------------------------------------
st.sidebar.markdown("# RETAIL ANALYTICS")
st.sidebar.markdown("---")
st.sidebar.caption("PERFORMANCE OVERVIEW")

section = st.sidebar.radio(
    "Navigate",
    [
        "Executive Overview",
        "Merchandising",
        "Supplier Performance",
        "Inventory Health",
    ],
    label_visibility="collapsed",
)

st.sidebar.markdown("---")
st.sidebar.caption("Data period: 2023–2024")
st.sidebar.caption("Source: Supplied analytical datasets")

# --------------------------------------------------
# PAGE HEADER
# --------------------------------------------------
st.title("Retail Performance Analytics")
st.markdown(
    '<div class="dashboard-subtitle">'
    'A consolidated view of merchandising performance, '
    'supplier reliability, and inventory health.'
    '</div>',
    unsafe_allow_html=True,
)

# --------------------------------------------------
# EXECUTIVE OVERVIEW PLACEHOLDER
# --------------------------------------------------

if section == "Executive Overview":
    st.subheader("Executive Overview")
    st.caption(
        "Key indicators across sales, supplier reliability, "
        "and inventory exposure."
    )

    # Headline KPIs
    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Recorded Revenue",
        f"₹{total_revenue / 100000:.2f} L",
    )
    c2.metric(
        "Recorded Gross Profit",
        f"₹{total_gross_profit / 100000:.2f} L",
    )
    c3.metric(
        "Weighted Gross Margin",
        f"{weighted_margin:.2f}%",
    )
    c4.metric(
        "Supplier Delay Rate",
        f"{supplier_delay_rate:.2f}%",
    )

    st.markdown("")

    c5, c6, c7, c8 = st.columns(4)

    c5.metric("Units Sold", f"{total_units:,.0f}")
    c6.metric("Average Discount", f"{avg_discount:.2f}%")
    c7.metric("Provisional Return Rate", f"{return_rate:.2f}%")
    c8.metric("Inventory Value", f"₹{inventory_value / 100000:.2f} L")

    st.caption(
        f"Inventory snapshot: {latest_snapshot:%d %b %Y} | "
        f"{inventory_sku_count} SKUs represented. "
        "Inventory value excludes SKUs without a record on this date."
    )

    st.markdown("---")
    st.subheader("Business Performance Areas")

    left, middle, right = st.columns(3)

    with left:
        st.markdown("### Merchandising")
        st.write(
            "Understand category profitability, brand performance, "
            "discounting, and recorded sales."
        )

    with middle:
        st.markdown("### Supplier Performance")
        st.write(
            "Identify late deliveries and review supplier "
            "fulfilment and lead times."
        )

    with right:
        st.markdown("### Inventory Health")
        st.write(
            "Locate high-value stock and investigate potential "
            "overstock exposure."
        )

    st.info(
        "Data note: Sales revenue and gross profit are recorded values. "
        "Return adjustments have not been validated, so these are not "
        "confirmed net sales or net profit."
    )


elif section == "Merchandising":

    # ==================================================
    # PAGE HEADER
    # ==================================================
    st.subheader("Merchandising Performance")
    st.caption(
        "Analyse sales contribution, product profitability, "
        "discounting, and return patterns."
    )

    # ==================================================
    # PREPARE DATA
    # ==================================================
    merch = sales.copy()

    merch["sale_date"] = pd.to_datetime(
        merch["sale_date"],
        dayfirst=True,
        errors="coerce",
    )

    # ==================================================
    # FILTERS
    # ==================================================
    st.markdown("#### Analysis filters")

    f1, f2, f3 = st.columns(3)

    categories = sorted(merch["category"].dropna().unique())
    brands = sorted(merch["brand"].dropna().unique())

    with f1:
        selected_categories = st.multiselect(
            "Category",
            options=categories,
            default=categories,
            key="merch_categories",
        )

    with f2:
        selected_brands = st.multiselect(
            "Brand",
            options=brands,
            default=brands,
            key="merch_brands",
        )

    valid_dates = merch["sale_date"].dropna()

    if valid_dates.empty:
        st.error("No valid sales dates were found.")
        st.stop()

    with f3:
        date_range = st.date_input(
            "Sales date range",
            value=(
                valid_dates.min().date(),
                valid_dates.max().date(),
            ),
            min_value=valid_dates.min().date(),
            max_value=valid_dates.max().date(),
            key="merch_dates",
        )

    if len(date_range) != 2:
        st.info("Select both a start date and an end date.")
        st.stop()

    start_date, end_date = date_range

    if start_date > end_date:
        st.error("Start date must be before end date.")
        st.stop()

    merch = merch[
        merch["category"].isin(selected_categories)
        & merch["brand"].isin(selected_brands)
        & merch["sale_date"].between(
            pd.Timestamp(start_date),
            pd.Timestamp(end_date),
        )
    ].copy()

    if merch.empty:
        st.warning("No sales records match the selected filters.")
        st.stop()

    # ==================================================
    # FILTERED KPIs
    # ==================================================
    recorded_revenue = merch["revenue"].sum()
    recorded_profit = merch["gross_profit"].sum()
    units_sold = merch["quantity"].sum()

    weighted_margin = (
        recorded_profit / recorded_revenue * 100
        if recorded_revenue else 0
    )

    avg_discount = merch["discount_pct"].mean()

    returned_records = merch["is_returned"].eq(1).sum()
    return_rate = (
        returned_records / len(merch) * 100
        if len(merch) else 0
    )

    st.markdown("---")
    st.markdown("#### Performance summary")

    k1, k2, k3, k4 = st.columns(4)

    k1.metric(
        "Recorded Revenue",
        f"₹{recorded_revenue / 100000:.2f} L",
    )
    k2.metric(
        "Recorded Gross Profit",
        f"₹{recorded_profit / 100000:.2f} L",
    )
    k3.metric(
        "Weighted Gross Margin",
        f"{weighted_margin:.2f}%",
    )
    k4.metric(
        "Units Sold",
        f"{units_sold:,.0f}",
    )

    k5, k6 = st.columns(2)

    k5.metric("Average Transaction Discount", f"{avg_discount:.2f}%")
    k6.metric("Provisional Return Rate", f"{return_rate:.2f}%")

    # ==================================================
    # CATEGORY PERFORMANCE
    # ==================================================
    st.markdown("---")
    st.markdown("#### Category performance")

    category_perf = (
        merch.groupby("category")
        .agg(
            recorded_revenue=("revenue", "sum"),
            gross_profit=("gross_profit", "sum"),
            units_sold=("quantity", "sum"),
            transactions=("sale_id", "nunique"),
        )
        .reset_index()
    )

    category_perf["gross_margin_pct"] = (
        category_perf["gross_profit"]
        / category_perf["recorded_revenue"].replace(0, float("nan"))
        * 100
    )

    category_perf = category_perf.sort_values(
        "recorded_revenue",
        ascending=False,
    )

    left, right = st.columns(2)

    with left:
        fig = px.bar(
            category_perf,
            x="category",
            y="recorded_revenue",
            title="Recorded revenue by category",
            labels={
                "category": "Category",
                "recorded_revenue": "Recorded revenue (₹)",
            },
            color_discrete_sequence=[BLUE],
        )
        fig.update_traces(
            hovertemplate="%{x}<br>Revenue: ₹%{y:,.0f}<extra></extra>"
        )
        st.plotly_chart(
            style_chart(fig),
            use_container_width=True,
        )

    with right:
        fig = px.bar(
            category_perf.sort_values("gross_profit"),
            x="gross_profit",
            y="category",
            orientation="h",
            title="Gross profit by category",
            labels={
                "category": "Category",
                "gross_profit": "Gross profit (₹)",
            },
            color_discrete_sequence=[NAVY],
        )
        fig.update_traces(
            hovertemplate="%{y}<br>Gross profit: ₹%{x:,.0f}<extra></extra>"
        )
        st.plotly_chart(
            style_chart(fig),
            use_container_width=True,
        )

    st.dataframe(
        category_perf.rename(
            columns={
                "category": "Category",
                "recorded_revenue": "Recorded revenue (₹)",
                "gross_profit": "Gross profit (₹)",
                "units_sold": "Units sold",
                "transactions": "Transactions",
                "gross_margin_pct": "Weighted margin (%)",
            }
        ).style.format({
            "Recorded revenue (₹)": "₹{:,.2f}",
            "Gross profit (₹)": "₹{:,.2f}",
            "Units sold": "{:,.0f}",
            "Transactions": "{:,.0f}",
            "Weighted margin (%)": "{:.2f}%",
        }),
        use_container_width=True,
        hide_index=True,
    )

    # ==================================================
    # DISCOUNT ANALYSIS
    # ==================================================
    st.markdown("---")
    st.markdown("#### Discount effectiveness")

    discount_edges = [-0.01, 10, 20, 30, 40, 100]
    discount_labels = [
        "0–10%", "10–20%", "20–30%", "30–40%", "40%+"
    ]

    merch["discount_band"] = pd.cut(
        merch["discount_pct"],
        bins=discount_edges,
        labels=discount_labels,
        include_lowest=True,
    )

    discount_perf = (
        merch.groupby("discount_band", observed=False)
        .agg(
            transactions=("sale_id", "nunique"),
            recorded_revenue=("revenue", "sum"),
            gross_profit=("gross_profit", "sum"),
            avg_discount=("discount_pct", "mean"),
        )
        .reset_index()
    )

    discount_perf["gross_margin_pct"] = (
        discount_perf["gross_profit"]
        / discount_perf["recorded_revenue"].replace(
            0, float("nan")
        )
        * 100
    )

    left, right = st.columns(2)

    with left:
        fig = px.bar(
            discount_perf,
            x="discount_band",
            y="gross_margin_pct",
            title="Weighted margin by discount band",
            labels={
                "discount_band": "Discount band",
                "gross_margin_pct": "Weighted margin (%)",
            },
            color_discrete_sequence=[RED],
        )
        fig.update_traces(
            hovertemplate="%{x}<br>Margin: %{y:.2f}%<extra></extra>"
        )
        st.plotly_chart(
            style_chart(fig),
            use_container_width=True,
        )

    with right:
        fig = px.bar(
            discount_perf,
            x="discount_band",
            y="transactions",
            title="Transactions by discount band",
            labels={
                "discount_band": "Discount band",
                "transactions": "Transactions",
            },
            color_discrete_sequence=[BLUE],
        )
        st.plotly_chart(
            style_chart(fig),
            use_container_width=True,
        )

    # ==================================================
    # BRAND SCORECARD
    # ==================================================
    st.markdown("---")
    st.markdown("#### Brand performance")

    brand_perf = (
        merch.groupby("brand")
        .agg(
            recorded_revenue=("revenue", "sum"),
            gross_profit=("gross_profit", "sum"),
            units_sold=("quantity", "sum"),
            transactions=("sale_id", "nunique"),
        )
        .reset_index()
    )

    brand_perf["gross_margin_pct"] = (
        brand_perf["gross_profit"]
        / brand_perf["recorded_revenue"].replace(
            0, float("nan")
        )
        * 100
    )

    brand_perf = brand_perf.sort_values(
        "recorded_revenue",
        ascending=False,
    )

    st.dataframe(
        brand_perf.rename(
            columns={
                "brand": "Brand",
                "recorded_revenue": "Recorded revenue (₹)",
                "gross_profit": "Gross profit (₹)",
                "units_sold": "Units sold",
                "transactions": "Transactions",
                "gross_margin_pct": "Weighted margin (%)",
            }
        ).style.format({
            "Recorded revenue (₹)": "₹{:,.2f}",
            "Gross profit (₹)": "₹{:,.2f}",
            "Units sold": "{:,.0f}",
            "Transactions": "{:,.0f}",
            "Weighted margin (%)": "{:.2f}%",
        }),
        use_container_width=True,
        hide_index=True,
    )

    # ==================================================
    # AUTOMATED BUSINESS OBSERVATIONS
    # ==================================================
    st.markdown("---")
    st.markdown("#### Business observations")

    best_revenue_category = category_perf.iloc[0]
    best_profit_category = category_perf.loc[
        category_perf["gross_profit"].idxmax()
    ]
    best_margin_category = category_perf.loc[
        category_perf["gross_margin_pct"].idxmax()
    ]

    render_insight(
        "Category performance",
        f"{best_revenue_category['category']} leads recorded revenue at "
        f"₹{best_revenue_category['recorded_revenue']:,.0f}. "
        f"{best_profit_category['category']} contributes the highest "
        f"recorded gross profit at "
        f"₹{best_profit_category['gross_profit']:,.0f}. "
        f"{best_margin_category['category']} has the highest weighted "
        f"category margin at {best_margin_category['gross_margin_pct']:.2f}%."
    )

    # Highest-margin discount band, using aggregated gross profit / revenue.
    valid_discount_bands = discount_perf[
        discount_perf["recorded_revenue"].gt(0)
        & discount_perf["gross_margin_pct"].notna()
    ]

    if not valid_discount_bands.empty:
        best_discount_band = valid_discount_bands.loc[
            valid_discount_bands["gross_margin_pct"].idxmax()
        ]
        render_insight(
            "Discount effectiveness",
            f"The {best_discount_band['discount_band']} discount band has "
            f"the highest weighted gross margin at "
            f"{best_discount_band['gross_margin_pct']:.2f}%, across "
            f"{best_discount_band['transactions']:,.0f} recorded transactions. "
            "Compare this with transaction volume and revenue before changing "
            "promotion strategy."
        )

    st.caption(
        "Interpretation note: differences across discount bands are "
        "associations, not proof that discounts alone caused margin changes. "
        "Returned transactions still contain positive recorded revenue and "
        "profit; net sales and net profit have not been established."
    )


elif section == "Supplier Performance":

    st.subheader("Supplier Performance")
    st.caption(
        "Assess supplier reliability, delivery delays, "
        "lead times, and order fulfilment."
    )

    # --------------------------------------------------
    # PREPARE DATA
    # --------------------------------------------------
    supplier_data = purchase_orders.copy()

    for col in ["po_date", "expected_delivery", "actual_delivery"]:
        supplier_data[col] = pd.to_datetime(
            supplier_data[col],
            errors="coerce",
        )

    supplier_data["delay_days_calculated"] = (
        supplier_data["actual_delivery"]
        - supplier_data["expected_delivery"]
    ).dt.days

    supplier_data["is_delayed_calculated"] = (
        supplier_data["delay_days_calculated"] > 0
    )

    supplier_data["late_days_only"] = (
        supplier_data["delay_days_calculated"]
        .where(supplier_data["is_delayed_calculated"])
    )

    # --------------------------------------------------
    # FILTERS
    # --------------------------------------------------
    st.markdown("#### Analysis filters")

    f1, f2 = st.columns(2)

    supplier_options = sorted(
        supplier_data["supplier"].dropna().unique()
    )

    with f1:
        selected_suppliers = st.multiselect(
            "Supplier",
            options=supplier_options,
            default=supplier_options,
            key="supplier_filter",
        )

    valid_po_dates = supplier_data["po_date"].dropna()

    with f2:
        if valid_po_dates.empty:
            st.error("No valid purchase-order dates were found.")
            st.stop()

        po_date_range = st.date_input(
            "Purchase-order date range",
            value=(
                valid_po_dates.min().date(),
                valid_po_dates.max().date(),
            ),
            min_value=valid_po_dates.min().date(),
            max_value=valid_po_dates.max().date(),
            key="po_date_filter",
        )

    if len(po_date_range) != 2:
        st.info("Select both a start date and an end date.")
        st.stop()

    po_start, po_end = po_date_range

    if po_start > po_end:
        st.error("Start date must be before end date.")
        st.stop()

    supplier_data = supplier_data[
        supplier_data["supplier"].isin(selected_suppliers)
        & supplier_data["po_date"].between(
            pd.Timestamp(po_start),
            pd.Timestamp(po_end),
        )
    ].copy()

    if supplier_data.empty:
        st.warning("No purchase orders match the selected filters.")
        st.stop()

    # --------------------------------------------------
    # KPI CALCULATIONS
    # --------------------------------------------------
    total_pos = len(supplier_data)

    delayed_pos = supplier_data[
        supplier_data["is_delayed_calculated"]
    ]

    delay_rate = (
        len(delayed_pos) / total_pos * 100
        if total_pos else 0
    )

    avg_late_days = delayed_pos[
        "delay_days_calculated"
    ].mean()

    avg_lead_time = supplier_data[
        "lead_time_days"
    ].mean()

    # Overall quantity-weighted fulfilment
    total_ordered = supplier_data["qty_ordered"].sum()
    total_received = supplier_data["qty_received"].sum()

    fulfilment_rate = (
        total_received / total_ordered * 100
        if total_ordered else 0
    )

    total_po_value = supplier_data["po_value"].sum()

    # --------------------------------------------------
    # KPI CARDS
    # --------------------------------------------------
    st.markdown("---")
    st.markdown("#### Procurement overview")

    k1, k2, k3, k4 = st.columns(4)

    k1.metric("Purchase Orders", f"{total_pos:,}")
    k2.metric("Delay Rate", f"{delay_rate:.2f}%")
    k3.metric(
        "Average Delay Among Late Orders",
        f"{avg_late_days:.2f} days"
        if pd.notna(avg_late_days) else "N/A",
    )
    k4.metric(
        "Weighted Fulfilment Rate",
        f"{fulfilment_rate:.2f}%",
    )

    k5, k6 = st.columns(2)

    k5.metric(
        "Average Lead Time",
        f"{avg_lead_time:.2f} days",
    )
    k6.metric(
        "Total PO Value",
        f"₹{total_po_value / 100000:.2f} L",
    )

    # --------------------------------------------------
    # SUPPLIER SCORECARD
    # --------------------------------------------------
    st.markdown("---")
    st.markdown("#### Supplier scorecard")

    scorecard = (
        supplier_data.groupby("supplier")
        .agg(
            purchase_orders=("po_id", "nunique"),
            delayed_orders=("is_delayed_calculated", "sum"),
            avg_lead_time_days=("lead_time_days", "mean"),
            avg_fulfilment_pct=("fulfillment_rate", "mean"),
            total_po_value=("po_value", "sum"),
        )
        .reset_index()
    )

    scorecard["delay_rate_pct"] = (
        scorecard["delayed_orders"]
        / scorecard["purchase_orders"]
        * 100
    )

    scorecard["avg_late_days"] = (
        supplier_data[
            supplier_data["is_delayed_calculated"]
        ]
        .groupby("supplier")["delay_days_calculated"]
        .mean()
        .reindex(scorecard["supplier"])
        .to_numpy()
    )

    scorecard = scorecard.sort_values(
        "delay_rate_pct",
        ascending=False,
    )

    left, right = st.columns(2)

    with left:
        fig = px.bar(
            scorecard.sort_values("delay_rate_pct"),
            x="delay_rate_pct",
            y="supplier",
            orientation="h",
            title="Delay rate by supplier",
            labels={
                "supplier": "Supplier",
                "delay_rate_pct": "Delayed orders (%)",
            },
            color_discrete_sequence=[RED],
        )
        fig.update_traces(
            hovertemplate="%{y}<br>Delay rate: %{x:.2f}%<extra></extra>"
        )
        st.plotly_chart(
            style_chart(fig, height=430),
            use_container_width=True,
        )

    with right:
        fig = px.bar(
            scorecard.sort_values("avg_late_days"),
            x="avg_late_days",
            y="supplier",
            orientation="h",
            title="Average lateness among delayed orders",
            labels={
                "supplier": "Supplier",
                "avg_late_days": "Average late days",
            },
            color_discrete_sequence=[BLUE],
        )
        fig.update_traces(
            hovertemplate="%{y}<br>Average lateness: %{x:.2f} days<extra></extra>"
        )
        st.plotly_chart(
            style_chart(fig, height=430),
            use_container_width=True,
        )

    st.dataframe(
        scorecard.rename(
            columns={
                "supplier": "Supplier",
                "purchase_orders": "Purchase orders",
                "delayed_orders": "Delayed orders",
                "delay_rate_pct": "Delay rate (%)",
                "avg_late_days": "Average late days",
                "avg_lead_time_days": "Average lead time (days)",
                "avg_fulfilment_pct": "Average fulfilment (%)",
                "avg_fulfillment_pct": "Average fulfilment (%)",
                "total_po_value": "Total PO value (₹)",
            }
        ).style.format({
            "Purchase orders": "{:,.0f}",
            "Delayed orders": "{:,.0f}",
            "Delay rate (%)": "{:.2f}%",
            "Average late days": "{:.2f}",
            "Average lead time (days)": "{:.2f}",
            "Average fulfilment (%)": "{:.2f}%",
            "Total PO value (₹)": "₹{:,.0f}",
        }),
        use_container_width=True,
        hide_index=True,
    )

    # --------------------------------------------------
    # BUSINESS OBSERVATIONS
    # --------------------------------------------------
    st.markdown("---")
    st.markdown("#### Business observations")

    highest_delay = scorecard.iloc[0]
    lowest_delay = scorecard.iloc[-1]

    render_insight(
        "Supplier reliability",
        f"{highest_delay['supplier']} has the highest delay rate at "
        f"{highest_delay['delay_rate_pct']:.2f}% in the current selection, "
        f"while {lowest_delay['supplier']} has the lowest rate at "
        f"{lowest_delay['delay_rate_pct']:.2f}%. "
        "Review late-order patterns and lead times before changing supplier "
        "allocation or replenishment plans."
    )

    st.caption(
        "Delay rate is calculated from actual versus expected delivery dates. "
        "Average late days includes only delayed orders. Overall fulfilment "
        "is quantity-weighted; supplier-level fulfilment in the scorecard "
        "is the mean of the existing row-level fulfilment metric."
    )


elif section == "Inventory Health":

    st.subheader("Inventory Health")
    st.caption(
        "Review stock exposure, inventory classification, "
        "and SKU-level replenishment indicators."
    )

    # --------------------------------------------------
    # PREPARE INVENTORY DATA
    # --------------------------------------------------
    inv = inventory.copy()

    inv["snapshot_date"] = pd.to_datetime(
        inv["snapshot_date"],
        format="%Y-%m-%d",
        errors="coerce",
    )

    for col in [
        "closing_stock",
        "reorder_point",
        "weeks_of_cover",
        "inventory_value",
        "stockout_flag",
    ]:
        inv[col] = pd.to_numeric(inv[col], errors="coerce")

    inv = inv.dropna(subset=["snapshot_date"])

    if inv.empty:
        st.error("No valid inventory snapshot dates were found.")
        st.stop()

    latest_snapshot = inv["snapshot_date"].max()

    # Use a consistent date for comparison across SKUs.
    latest_inv = inv[
        inv["snapshot_date"] == latest_snapshot
    ].copy()

    # --------------------------------------------------
    # FILTERS
    # --------------------------------------------------
    st.markdown("#### Analysis filters")

    f1, f2 = st.columns(2)

    categories = sorted(latest_inv["category"].dropna().unique())
    brands = sorted(latest_inv["brand"].dropna().unique())

    with f1:
        selected_categories = st.multiselect(
            "Category",
            categories,
            default=categories,
            key="inventory_categories",
        )

    with f2:
        selected_brands = st.multiselect(
            "Brand",
            brands,
            default=brands,
            key="inventory_brands",
        )

    latest_inv = latest_inv[
        latest_inv["category"].isin(selected_categories)
        & latest_inv["brand"].isin(selected_brands)
    ].copy()

    if latest_inv.empty:
        st.warning("No SKUs match the selected filters.")
        st.stop()

    # --------------------------------------------------
    # KPI CALCULATIONS
    # --------------------------------------------------
    total_inventory_value = latest_inv["inventory_value"].sum()
    total_closing_stock = latest_inv["closing_stock"].sum()
    sku_count = latest_inv["sku_id"].nunique()

    overstock_count = latest_inv[
        latest_inv["inventory_health"] == "Overstock"
    ]["sku_id"].nunique()

    low_or_critical_count = latest_inv[
        latest_inv["inventory_health"].isin(["Low", "Critical"])
    ]["sku_id"].nunique()

    # --------------------------------------------------
    # KPI CARDS
    # --------------------------------------------------
    st.markdown("---")
    st.markdown("#### Inventory overview")

    k1, k2, k3, k4 = st.columns(4)

    k1.metric(
        "Inventory Value",
        f"₹{total_inventory_value / 100000:.2f} L",
    )
    k2.metric("Closing Stock", f"{total_closing_stock:,.0f} units")
    k3.metric("SKUs Represented", f"{sku_count}")
    k4.metric("Overstock SKUs", f"{overstock_count}")

    st.caption(
        f"Snapshot date: {latest_snapshot:%d %b %Y}. "
        f"Low or critical SKUs in this selection: {low_or_critical_count}. "
        "SKUs without a record on this date are excluded."
    )

    # --------------------------------------------------
    # INVENTORY VALUE BY SKU
    # --------------------------------------------------
    st.markdown("---")
    st.markdown("#### Inventory exposure by SKU")

    sku_perf = latest_inv.sort_values(
        "inventory_value",
        ascending=True,
    )

    fig = px.bar(
        sku_perf,
        x="inventory_value",
        y="sku_id",
        orientation="h",
        color="inventory_health",
        title="Inventory value by SKU",
        labels={
            "inventory_value": "Inventory value (₹)",
            "sku_id": "SKU",
            "inventory_health": "Inventory health",
        },
        color_discrete_map={
            "Overstock": RED,
            "Healthy": BLUE,
            "Low": "#D9A441",
            "Critical": "#8F1D25",
        },
    )

    fig.update_traces(
        hovertemplate=(
            "%{y}<br>Inventory value: ₹%{x:,.0f}"
            "<extra></extra>"
        )
    )

    st.plotly_chart(
        style_chart(fig, height=420),
        use_container_width=True,
    )

    # --------------------------------------------------
    # STOCK AND COVER TABLE
    # --------------------------------------------------
    st.markdown("---")
    st.markdown("#### SKU-level stock position")

    inventory_table = latest_inv[
        [
            "sku_id",
            "brand",
            "category",
            "snapshot_date",
            "closing_stock",
            "reorder_point",
            "weeks_of_cover",
            "inventory_health",
            "inventory_value",
        ]
    ].sort_values("inventory_value", ascending=False)

    st.dataframe(
        inventory_table.rename(
            columns={
                "sku_id": "SKU",
                "brand": "Brand",
                "category": "Category",
                "snapshot_date": "Snapshot date",
                "closing_stock": "Closing stock (units)",
                "reorder_point": "Reorder point",
                "weeks_of_cover": "Reported weeks of cover",
                "inventory_health": "Inventory health",
                "inventory_value": "Inventory value (₹)",
            }
        ).style.format({
            "Closing stock (units)": "{:,.0f}",
            "Reorder point": "{:,.0f}",
            "Reported weeks of cover": "{:.1f}",
            "Inventory value (₹)": "₹{:,.0f}",
        }),
        use_container_width=True,
        hide_index=True,
    )

    # --------------------------------------------------
    # INVENTORY HEALTH DISTRIBUTION
    # --------------------------------------------------
    st.markdown("---")
    st.markdown("#### Inventory classification")

    health_counts = (
        latest_inv.groupby("inventory_health")["sku_id"]
        .nunique()
        .reset_index(name="sku_count")
    )

    fig = px.bar(
        health_counts,
        x="inventory_health",
        y="sku_count",
        title="SKUs by inventory health classification",
        labels={
            "inventory_health": "Inventory health",
            "sku_count": "Number of SKUs",
        },
        color="inventory_health",
        color_discrete_map={
            "Overstock": RED,
            "Healthy": BLUE,
            "Low": "#D9A441",
            "Critical": "#8F1D25",
        },
    )

    st.plotly_chart(
        style_chart(fig, height=320),
        use_container_width=True,
    )

    # --------------------------------------------------
    # BUSINESS OBSERVATIONS
    # --------------------------------------------------
    st.markdown("---")
    st.markdown("#### Business observations")

    highest_value_sku = latest_inv.loc[
        latest_inv["inventory_value"].idxmax()
    ]

    health_summary = (
        latest_inv.groupby("inventory_health")["sku_id"]
        .nunique()
        .sort_values(ascending=False)
    )
    health_text = ", ".join(
        f"{health}: {count}"
        for health, count in health_summary.items()
    )

    render_insight(
        "Inventory exposure",
        f"SKU {highest_value_sku['sku_id']} has the highest inventory value "
        f"at ₹{highest_value_sku['inventory_value']:,.0f} on the selected "
        f"snapshot date. {overstock_count} of {sku_count} represented SKUs "
        f"are classified as Overstock. Current health distribution: "
        f"{health_text}. Review demand patterns and replenishment parameters "
        "before making stock reduction decisions."
    )

    st.caption(
        "Limitations: weeks of cover is based on snapshot-level sales "
        "and may be volatile. Inventory health is an existing dataset "
        "classification, not independently validated ground truth. "
        "All historical stockout flags are zero, so stockout performance "
        "cannot be compared using this dataset."
    )


st.markdown("---")
st.caption(
    "Analytical prototype | Figures are subject to "
    "the data validation notes documented in the project."
)
