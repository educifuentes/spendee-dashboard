"""
Data transformation and aggregation functions for the dashboard.
"""
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta


def load_clean_data():
    """Load cleaned expense data."""
    data_path = Path(__file__).parent.parent / "data" / "clean" / "expenses_main-clp_clean.csv"
    df = pd.read_csv(data_path)
    print(f"Data loaded successfully: {df.shape[0]} rows, {df.shape[1]} columns")
    
    df["date"] = pd.to_datetime(df["date"])
    print(f"Date column cast to pandas datetime format: {df['date'].dtype}")
    return df


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


def get_current_month_expenses(df):
    """Get total expenses for current month."""
    now = datetime.now()
    start = datetime(now.year, now.month, 1)
    end = now
    current_month = filter_by_date_range(df, start, end)
    return current_month["amount"].sum()


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
    return last_month["amount"].sum()


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


def get_top_expenses_by_label(df, n=10, year=None, month=None):
    """Get top N expenses aggregated by label for a given month (default: current month)."""
    if year is None:
        year = datetime.now().year
    if month is None:
        month = datetime.now().month
    
    filtered = df[(df["date"].dt.year == year) & (df["date"].dt.month == month)].copy()
    
    # Expand labels (split comma-separated labels) and preserve category
    label_expanded = []
    for _, row in filtered.iterrows():
        if pd.notna(row["labels"]) and row["labels"]:
            labels_list = [l.strip() for l in str(row["labels"]).split(",")]
            for label in labels_list:
                label_expanded.append({
                    "label": label,
                    "amount": row["amount"],
                    "category": row["category"]
                })
    
    if not label_expanded:
        return pd.DataFrame(columns=["label", "amount", "category"])
    
    # Group by label, sum amounts, and get most common category
    label_df = pd.DataFrame(label_expanded)
    label_totals = label_df.groupby("label").agg({
        "amount": "sum",
        "category": lambda x: x.mode().iloc[0] if len(x.mode()) > 0 else x.iloc[0]  # Most common category
    }).reset_index()
    label_totals = label_totals.sort_values("amount", ascending=False).head(n)
    label_totals = label_totals.sort_values("amount", ascending=True)  # For horizontal bar chart
    return label_totals


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
    
    # Sort chronologically by date
    periods = periods.sort_values("date")
    return periods[["period_label", "period_value"]].to_dict("records")

