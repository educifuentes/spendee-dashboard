import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime


def format_currency_columns(df: pd.DataFrame, currency: str = "CLP") -> pd.DataFrame:
    """
    Format all numeric columns (int or float) in a dataframe as currency.
    
    Args:
        df: Input DataFrame
        currency: Currency type, either "CLP" or "USD" (default: "CLP")
    
    Returns:
        DataFrame with numeric columns formatted as currency strings
    
    Examples:
        >>> df = pd.DataFrame({'amount': [1000.5, 2000.75], 'count': [5, 10]})
        >>> format_currency_columns(df, currency="CLP")
        >>> # Returns DataFrame with 'amount' and 'count' formatted as "CLP 1,001", "CLP 2,001", etc.
    """
    df = df.copy()
    
    # Find all numeric columns (int and float)
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    
    if currency.upper() == "CLP":
        # CLP: no decimal places, use comma as thousands separator
        for col in numeric_cols:
            df[col] = df[col].apply(
                lambda x: f"CLP {x:,.0f}" if pd.notna(x) else x
            )
    elif currency.upper() == "USD":
        # USD: 2 decimal places, use comma as thousands separator
        for col in numeric_cols:
            df[col] = df[col].apply(
                lambda x: f"${x:,.2f}" if pd.notna(x) else x
            )
    else:
        raise ValueError(f"Unsupported currency: {currency}. Use 'CLP' or 'USD'.")
    
    return df


def setup_period_selection(df: pd.DataFrame, get_available_periods_func, granularity_key: str = "granularity", selected_period_key: str = "selected_period_label"):
    """
    Set up and simplify period selection logic for the dashboard.
    Ensures periods are always sorted descending (most recent first).
    
    Args:
        df: Transaction DataFrame
        get_available_periods_func: Function that returns sorted periods
        granularity_key: Session state key for granularity (Month/Week/Year)
        selected_period_key: Session state key for the selected period label
    """
    # 1. Initialize/Sync granularity
    granularity = st.session_state.setdefault(granularity_key, "Month")
    
    # 2. Get available periods (already sorted descending by date in transforms.py)
    periods = get_available_periods_func(df, granularity)
    options = [p["period_label"] for p in periods]
    values = {p["period_label"]: p["period_value"] for p in periods}
    
    if not options:
        return granularity, "", [], {}, 0

    # 3. Determine current selection and default fallback
    current_val = st.session_state.get(selected_period_key)
    
    if current_val not in options:
        # Default to current month if in Month view, otherwise use most recent (index 0)
        now_label = datetime.now().strftime("%B %Y")
        st.session_state[selected_period_key] = now_label if (granularity == "Month" and now_label in options) else options[0]
        
    selected_label = st.session_state[selected_period_key]
    default_index = options.index(selected_label)
    
    return granularity, selected_label, options, values, default_index


def get_wallet_options(df, include_all: bool = True):
    """
    Get wallet options from transaction DataFrame.
    
    Args:
        df: DataFrame with transactions, must have a 'wallet' column
        include_all: If True, adds "All" as the first option (default: True)
    
    Returns:
        list: List of wallet options, optionally starting with "All"
    """
    wallet_options = sorted(df["wallet"].unique().tolist())
    
    if include_all:
        wallet_options = ["All"] + wallet_options
    
    return wallet_options