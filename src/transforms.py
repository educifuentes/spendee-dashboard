"""
Data transformation and aggregation functions for the dashboard.
"""
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta


# ==========================================
# Data Loading
# ==========================================
def load_clean_data():
    """Load cleaned expense data."""
    data_path = Path(__file__).parent.parent / "data" / "clean" / "expenses_main-clp_clean.csv"
    df = pd.read_csv(data_path)
    print(f"Data loaded successfully: {df.shape[0]} rows, {df.shape[1]} columns")
    
    df["date"] = pd.to_datetime(df["date"])
    print(f"Date column cast to pandas datetime format: {df['date'].dtype}")
    return df


# ==========================================
# Data Transformation
# ==========================================
def create_period_columns(df):
    """Create day, week, month, year columns from date."""
    df["day"] = df["date"].dt.strftime("%Y-%m-%d")
    # Use isocalendar to correctly handle year boundaries for weeks
    iso = df["date"].dt.isocalendar()
    df["week"] = iso.year.astype(str) + "-W" + iso.week.astype(str).str.zfill(2)
    df["month"] = df["date"].dt.strftime("%Y-%m")
    df["year"] = df["date"].dt.year
    return df

def create_universal_amount(df):
    """
    Create amount_universal column in CLP.
    If currency is USD, converts to CLP using approximate monthly rates.
    """
    if "currency" not in df.columns:
        df["amount_universal"] = df["amount"]
        return df

    # Approximate USD to CLP rates (First day of month)
    rates_path = Path(__file__).parent.parent / "constants" / "usd_clp_rates.csv"
    rates_df = pd.read_csv(rates_path)
    rates_map = dict(zip(rates_df["month"], rates_df["rate"]))

    df["rate"] = df["date"].dt.strftime("%Y-%m").map(rates_map).fillna(900)
    df["amount_universal_clp"] = df.apply(lambda x: x["amount"] * x["rate"] if x["currency"] == "USD" else x["amount"], axis=1).round(0)

    return df.drop(columns=["rate"])


# ==========================================
# Filtering Utilities
# ==========================================
def filter_by_date_range(df, start_date, end_date):
    """Filter dataframe by date range."""
    # Normalize timezone-aware dates to timezone-naive for comparison
    # This prevents TypeError when comparing datetime64[ns, UTC] with timezone-naive Timestamp
    df_dates = df["date"].dt.tz_localize(None) if df["date"].dt.tz is not None else df["date"]
    
    # Ensure start_date and end_date are timezone-naive Timestamps
    if isinstance(start_date, pd.Timestamp):
        start_date = start_date.tz_localize(None) if start_date.tz is not None else start_date
    else:
        start_date = pd.Timestamp(start_date)
    
    if isinstance(end_date, pd.Timestamp):
        end_date = end_date.tz_localize(None) if end_date.tz is not None else end_date
    else:
        end_date = pd.Timestamp(end_date)
    
    # Create mask using normalized dates
    mask = (df_dates >= start_date) & (df_dates <= end_date)
    return df[mask].copy()

def filter_by_category(df, categories):
    """Filter dataframe by categories."""
    if not categories or len(categories) == 0:
        return df
    return df[df["category"].isin(categories)].copy()


def filter_by_label(df, labels):
    """Filter dataframe by labels."""
    if not labels or len(labels) == 0:
        return df
    # Labels column might contain comma-separated values
    mask = df["labels"].notna()
    if mask.any():
        # Check if any of the selected labels appear in the labels column
        label_mask = df["labels"].str.contains("|".join(labels), case=False, na=False)
        return df[label_mask].copy()
    return df


# ==========================================
# Period & Date Helpers
# ==========================================
def get_available_periods(df, period_type):
    """Get available periods from dataframe, formatted and sorted chronologically."""
    df_copy = df.copy()
    
    if period_type == "Month":
        # Group by year-month, format as "Month Year"
        df_copy["period_key"] = df_copy["date"].dt.to_period("M")
        periods = df_copy.groupby("period_key")["date"].first().reset_index()
        periods["period_label"] = periods["period_key"].apply(lambda p: p.strftime("%B %Y"))
        periods["period_value"] = periods["period_key"].astype(str)
    elif period_type == "Week":
        # Group by ISO week, get Monday of the week, format as "Month Day, Year"
        df_copy["year"] = df_copy["date"].dt.isocalendar().year
        df_copy["week"] = df_copy["date"].dt.isocalendar().week
        df_copy["period_key"] = df_copy["year"].astype(str) + "-W" + df_copy["week"].astype(str).str.zfill(2)
        
        # Calculate Monday of each week
        periods = df_copy.groupby("period_key")["date"].first().reset_index()
        periods["monday"] = periods["date"].apply(lambda d: d - pd.Timedelta(days=d.weekday()))
        # Format as "Month Day, Year" (handle day without leading zero)
        periods["period_label"] = periods["monday"].apply(lambda d: f"{d.strftime('%B')} {d.day}, {d.year}")
        periods["period_value"] = periods["period_key"]
    else:  # Year
        df_copy["period_key"] = df_copy["date"].dt.year
        periods = df_copy.groupby("period_key")["date"].first().reset_index()
        periods["period_label"] = periods["period_key"].astype(str)
        periods["period_value"] = periods["period_key"].astype(str)
    
    # Sort chronologically by date (descending - most recent first)
    periods = periods.sort_values("date", ascending=False)
    return periods[["period_label", "period_value"]].to_dict("records")

def get_period_dates(granularity, selected_period_value):
    """
    Calculate start and end dates based on granularity and period value.
    
    Args:
        granularity: "Month", "Week", or "Year"
        selected_period_value: String representation of the period (e.g. "2023-01", "2023-W01", "2023")
        
    Returns:
        tuple: (start_date, end_date) as pandas Timestamps
    """
    if granularity == "Month":
        # Parse YYYY-MM format
        year, month = map(int, selected_period_value.split("-"))
        start_date = pd.Timestamp(year=year, month=month, day=1)
        # Get last day of month
        if month == 12:
            end_date = pd.Timestamp(year=year+1, month=1, day=1) - pd.Timedelta(days=1)
        else:
            end_date = pd.Timestamp(year=year, month=month+1, day=1) - pd.Timedelta(days=1)
        end_date = end_date.replace(hour=23, minute=59, second=59)
    elif granularity == "Week":
        # Parse YYYY-WXX format, get Monday and Sunday of that week
        year, week = selected_period_value.split("-W")
        year, week = int(year), int(week)
        # Get Monday of the week
        start_date = pd.Timestamp.fromisocalendar(year, week, 1)
        end_date = start_date + pd.Timedelta(days=6, hours=23, minutes=59, seconds=59)
    else:  # Year
        year = int(selected_period_value)
        start_date = pd.Timestamp(year=year, month=1, day=1)
        end_date = pd.Timestamp(year=year, month=12, day=31, hour=23, minute=59, second=59)
        
    return start_date, end_date


# ==========================================
# KPI Metrics
# ==========================================
def get_current_month_expenses(df):
    """Get total expenses for current month."""
    now = datetime.now()
    start = datetime(now.year, now.month, 1)
    end = now
    current_month = filter_by_date_range(df, start, end)
    return current_month[current_month["type"] == "Expense"]["amount"].sum()


def get_current_month_income(df):
    """Get total income for current month."""
    now = datetime.now()
    start = datetime(now.year, now.month, 1)
    end = now
    current_month = filter_by_date_range(df, start, end)
    return current_month[current_month["type"] == "Income"]["amount"].sum()

def get_last_month_income(df):
    """Get total income for last month."""
    now = datetime.now()
    if now.month == 1:
        last_month_start = datetime(now.year - 1, 12, 1)
        last_month_end = datetime(now.year - 1, 12, 31, 23, 59, 59)
    else:
        last_month_start = datetime(now.year, now.month - 1, 1)
        last_month_end = datetime(now.year, now.month, 1) - timedelta(seconds=1)
    
    last_month = filter_by_date_range(df, last_month_start, last_month_end)
    return last_month[last_month["type"] == "Income"]["amount"].sum()



def get_last_month_expenses(df):
    """Get total expenses for last month."""
    now = datetime.now()
    if now.month == 1:
        last_month_start = datetime(now.year - 1, 12, 1)
        last_month_end = datetime(now.year - 1, 12, 31, 23, 59, 59)
    else:
        last_month_start = datetime(now.year, now.month - 1, 1)
        last_month_end = datetime(now.year, now.month, 1) - timedelta(seconds=1)
    
    last_month = filter_by_date_range(df, last_month_start, last_month_end)
    return last_month[last_month["type"] == "Expense"]["amount"].sum()


# ==========================================
# Chart Data Aggregations
# ==========================================
def get_expenses_by_category(df, start_date, end_date):
    """Get expenses aggregated by category for selected period."""
    filtered = filter_by_date_range(df, start_date, end_date)
    return filtered.groupby("category")["amount"].sum().reset_index().sort_values("amount", ascending=False)


def get_expenses_by_month(df, year=None):
    """Get expenses aggregated by month for a given year (default: current year)."""
    if year is None:
        year = datetime.now().year
    
    filtered = df[df["date"].dt.year == year].copy()
    filtered["month"] = filtered["date"].dt.month
    monthly = filtered.groupby("month")["amount"].sum().reset_index()
    monthly["month_name"] = monthly["month"].apply(lambda x: datetime(year, x, 1).strftime("%B"))
    return monthly.sort_values("month")


def get_top_transactions(df, n=10, year=None, month=None):
    """Get top N transactions for a given month (default: current month)."""
    if year is None:
        year = datetime.now().year
    if month is None:
        month = datetime.now().month
    
    filtered = df[(df["date"].dt.year == year) & (df["date"].dt.month == month)].copy()
    top = filtered.nlargest(n, "amount")[["date", "category", "amount", "note", "labels"]].copy()
    top = top.sort_values("amount", ascending=True)  # For horizontal bar chart
    return top

def get_transactions_by_category_sorted(df):
    """Get transactions aggregated by category with transaction counts."""
    res = df.groupby("category").agg(
        amount=("amount_universal_clp", "sum"),
        count=("date", "count")
    ).reset_index().sort_values("amount", ascending=False)

    res["transaction_label"] = res["count"].astype(str) + " transactions"

    res["amount"] = res["amount"].apply(lambda x: f"${x:,.0f}")
    return res.set_index("category").drop(columns=["count"])

def get_transactions_by_labels_sorted(df):
    """
    Get transactions aggregated by labels with transaction counts.
    Handles comma-separated labels by expanding them into separate rows.
    """
    # Filter rows with labels
    df_labels = df[df["labels"].notna() & (df["labels"].astype(str).str.strip() != "")].copy()
    
    if df_labels.empty:
        return pd.DataFrame(columns=["amount", "transaction_label"]).set_index(pd.Index([], name="labels"))

    # Expand comma-separated labels
    expanded = []
    for _, row in df_labels.iterrows():
        labels = [l.strip() for l in str(row["labels"]).split(",") if l.strip()]
        for label in labels:
            expanded.append({
                "label": label,
                "amount": row["amount_universal_clp"]
            })
            
    expanded_df = pd.DataFrame(expanded)
    
    # Aggregate by label
    res = expanded_df.groupby("label").agg(
        amount=("amount", "sum"),
        count=("amount", "count")
    ).reset_index().sort_values("amount", ascending=False)

    res["transaction_label"] = res["count"].astype(str) + " transactions"
    res["amount_fmt"] = res["amount"].apply(lambda x: f"${x:,.0f}")
    
    return res.rename(columns={"label": "labels", "amount_fmt": "amount"}).set_index("labels")[["amount", "transaction_label"]]



def get_categories_ranked_by_amount(df):
    """Get list of categories ranked by total amount (descending)."""
    return df.groupby("category")["amount_universal_clp"].sum().sort_values(ascending=False).index.tolist()

def get_top_expenses_by_label(df, n=10, year=None, month=None):
    """
    Get top N expenses aggregated by label for a given month (default: current month).
    Handles comma-separated labels by expanding them into separate rows.
    """
    if year is None: year = datetime.now().year
    if month is None: month = datetime.now().month
    
    # Filter by date and type
    mask = (df["date"].dt.year == year) & (df["date"].dt.month == month)
    if "type" in df.columns:
        mask &= (df["type"].str.lower() == "expense")
    
    filtered = df[mask].copy()
    
    # Filter rows with labels
    df_labels = filtered[filtered["labels"].notna() & (filtered["labels"].astype(str).str.strip() != "")].copy()
    
    if df_labels.empty:
        return pd.DataFrame(columns=["label", "amount", "category"])
    
    # Expand labels
    expanded = []
    for _, row in df_labels.iterrows():
        labels = [l.strip() for l in str(row["labels"]).split(",") if l.strip()]
        for label in labels:
            expanded.append({
                "label": label,
                "amount": row["amount_universal_clp"] if "amount_universal_clp" in row else row["amount"],
                "category": row["category"]
            })
    
    expanded_df = pd.DataFrame(expanded)
    
    # Group by label, sum amounts, and get most common category
    res = expanded_df.groupby("label").agg({
        "amount": "sum",
        "category": lambda x: x.mode().iloc[0] if not x.mode().empty else x.iloc[0]
    }).reset_index()
    
    # Sort for horizontal bar chart (top N, then ascending for Altair)
    res = res.sort_values("amount", ascending=False).head(n)
    return res.sort_values("amount", ascending=True)


def get_expenses_by_budget_month(df, start_date=None, end_date=None):
    """
    Get expenses aggregated by budget and month.
    Args:
        df: DataFrame with 'date', 'amount', and 'budget' columns
        start_date: Optional start date to filter (default: None for all data)
        end_date: Optional end date to filter (default: None for all data)
    Returns:
        DataFrame with columns: 'date', 'budget', 'amount' (date column preserved for Altair)
    """
    filtered = df.copy()
    
    # Apply date filters if provided
    if start_date is not None or end_date is not None:
        if start_date is None:
            start_date = filtered["date"].min()
        if end_date is None:
            end_date = filtered["date"].max()
        filtered = filter_by_date_range(filtered, start_date, end_date)
    
    # Keep date column for Altair's month() function
    # Group by date (will be aggregated by month in Altair) and budget
    result = filtered.groupby([filtered["date"].dt.to_period("M"), "budget"])["amount"].sum().reset_index()
    
    # Convert period back to datetime (first day of month) for Altair
    result["date"] = pd.to_datetime(result["date"].astype(str))
    
    return result[["date", "budget", "amount"]]
