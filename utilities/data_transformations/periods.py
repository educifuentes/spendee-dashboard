import pandas as pd

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
