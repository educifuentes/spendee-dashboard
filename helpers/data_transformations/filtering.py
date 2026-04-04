import pandas as pd

def filter_by_date_range(df, start_date, end_date):
    """Filter dataframe by date range."""
    # Normalize timezone-aware dates to timezone-naive for comparison
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
