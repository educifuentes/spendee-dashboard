import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta

def metric_expenses(df):
    """
    Calculates MTD expenses for the current month and the same period last month.
    Returns: (current_mtd_total, last_mtd_total, percentage_change)
    """
    # 1. Normalize dates
    df = df.copy()
    df["date_naive"] = df["date"].dt.tz_localize(None) if df["date"].dt.tz is not None else df["date"]
    
    # 2. Reference dates
    today = pd.Timestamp.now().normalize()
    # today = df["date_naive"].max() # Alternative: use max data date if 'today' is too far ahead
    
    # If today is in the future relative to data, we might want to use the last available day in current month
    # But usually 'today' is what we want for a dashboard.
    
    current_month_start = today.replace(day=1)
    
    # Same day last month
    last_month_today = today - relativedelta(months=1)
    last_month_start = last_month_today.replace(day=1)
    
    # 3. Filter Expenses
    expenses = df[df["type"] == "Expense"]
    
    # 4. Calculate Current MTD
    current_mtd = expenses[
        (expenses["date_naive"] >= current_month_start) & 
        (expenses["date_naive"] <= today)
    ]["amount"].sum()
    
    # 5. Calculate Last Monthly MTD (normalized to same day)
    last_mtd = expenses[
        (expenses["date_naive"] >= last_month_start) & 
        (expenses["date_naive"] <= last_month_today)
    ]["amount"].sum()
    
    # 6. Percentage Change
    pct_change = ((current_mtd - last_mtd) / last_mtd * 100) if last_mtd > 0 else 0
    
    return current_mtd, last_mtd, pct_change
