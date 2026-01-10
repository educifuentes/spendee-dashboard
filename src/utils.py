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
    Set up period selection logic for Streamlit dashboard.
    
    Args:
        df: DataFrame with transactions data
        get_available_periods_func: Function to get available periods (e.g., get_available_periods from transforms)
        granularity_key: Session state key for granularity (default: "granularity")
        selected_period_key: Session state key for selected period label (default: "selected_period_label")
    
    Returns:
        tuple: (granularity, selected_period_label, period_options, period_values, default_index)
    """
    # Initialize granularity in session state
    if granularity_key not in st.session_state:
        st.session_state[granularity_key] = "Month"
    
    granularity = st.session_state[granularity_key]
    
    # Get available periods and create options/values mappings
    available_periods = get_available_periods_func(df, granularity)
    period_options = [p["period_label"] for p in available_periods]
    period_values = {p["period_label"]: p["period_value"] for p in available_periods}
    
    # Get default index for selected period
    if selected_period_key not in st.session_state or st.session_state[selected_period_key] not in period_options:
        if granularity == "Month" and period_options:
            current_period_label = datetime.now().strftime("%B %Y")
            default_index = period_options.index(current_period_label) if current_period_label in period_options else len(period_options) - 1
        elif period_options:
            default_index = len(period_options) - 1
        else:
            default_index = 0
        st.session_state[selected_period_key] = period_options[default_index] if period_options else ""
    else:
        default_index = period_options.index(st.session_state[selected_period_key]) if st.session_state[selected_period_key] in period_options else 0
    
    selected_period_label = st.session_state[selected_period_key]
    
    return granularity, selected_period_label, period_options, period_values, default_index


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