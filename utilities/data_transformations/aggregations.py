import pandas as pd
from datetime import datetime, timedelta
from utilities.data_transformations.filtering import filter_by_date_range

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
        total_amount=("amount", "sum"),
        count=("amount", "count")
    ).reset_index().sort_values("total_amount", ascending=False)

    res["transaction_label"] = res["count"].astype(str) + " transactions"
    res["amount_fmt"] = res["total_amount"].apply(lambda x: f"${x:,.0f}")
    
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
