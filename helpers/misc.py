import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
from pandas.api.types import (
    is_categorical_dtype,
    is_datetime64_any_dtype,
    is_numeric_dtype,
    is_object_dtype,
)


def setup_period_selection(df: pd.DataFrame, get_available_periods_func, granularity_key: str = "granularity", selected_period_key: str = "selected_period_label"):
    """
    Set up and simplify period selection logic for the dashboard.
    Ensures periods are always sorted descending (most recent first).
    """
    # 1. Initialize/Sync granularity
    granularity = st.session_state.setdefault(granularity_key, "Month")
    
    # 2. Get available periods (already sorted descending by date in utilities/transforms.py)
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
    """
    wallet_options = sorted(df["wallet"].unique().tolist())
    
    if include_all:
        wallet_options = ["All"] + wallet_options
    
    return wallet_options


def st_dataframe_helper(
    df: pd.DataFrame, 
    selected_columns: list[str] = None, 
    date_columns: list[str] = None, 
    currency_columns: list[str] = None, 
    multiselect_columns: list[str] = None,
    **kwargs
):
    """
    Custom wrapper for st.dataframe that simplifies column configuration.
    """
    display_df = df.copy()
    if selected_columns:
        valid_cols = [c for c in selected_columns if c in display_df.columns]
        display_df = display_df[valid_cols]
    
    column_config = {}
    
    if date_columns:
        for col in date_columns:
            if col in display_df.columns:
                column_config[col] = st.column_config.DateColumn(col.replace("_", " ").title())
                
    if currency_columns:
        for col in currency_columns:
            if col in display_df.columns:
                column_config[col] = st.column_config.NumberColumn(
                    col.replace("_", " ").title(),
                    format="$ %d"
                )
                
    if multiselect_columns:
        for col in multiselect_columns:
            if col in display_df.columns:
                column_config[col] = st.column_config.MultiselectColumn(col.replace("_", " ").title())
    
    if "column_config" in kwargs:
        column_config.update(kwargs.pop("column_config"))
        
    st.dataframe(
        display_df,
        column_config=column_config,
        hide_index=kwargs.pop("hide_index", True),
        width=kwargs.pop("width", "stretch"),
        use_container_width=kwargs.pop("use_container_width", True),
        **kwargs
    )


def filter_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds a UI on top of a dataframe to let viewers filter columns.
    """
    modify = st.checkbox("Add filters")

    if not modify:
        return df

    df = df.copy()

    for col in df.columns:
        if is_object_dtype(df[col]):
            try:
                df[col] = pd.to_datetime(df[col])
            except Exception:
                pass

        if is_datetime64_any_dtype(df[col]):
            df[col] = df[col].dt.tz_localize(None)

    modification_container = st.container()

    with modification_container:
        to_filter_columns = st.multiselect("Filter dataframe on", df.columns)
        for column in to_filter_columns:
            left, right = st.columns((1, 20))
            left.write("↳")
            if is_categorical_dtype(df[column]) or df[column].nunique() < 10:
                user_cat_input = right.multiselect(
                    f"Values for {column}",
                    df[column].unique(),
                    default=list(df[column].unique()),
                )
                df = df[df[column].isin(user_cat_input)]
            elif is_numeric_dtype(df[column]):
                _min = float(df[column].min())
                _max = float(df[column].max())
                step = (_max - _min) / 100
                user_num_input = right.slider(
                    f"Values for {column}",
                    _min,
                    _max,
                    (_min, _max),
                    step=step,
                )
                df = df[df[column].between(*user_num_input)]
            elif is_datetime64_any_dtype(df[column]):
                user_date_input = right.date_input(
                    f"Values for {column}",
                    value=(
                        df[column].min(),
                        df[column].max(),
                    ),
                )
                if len(user_date_input) == 2:
                    user_date_input = tuple(map(pd.to_datetime, user_date_input))
                    start_date, end_date = user_date_input
                    df = df.loc[df[column].between(start_date, end_date)]
            else:
                user_text_input = right.text_input(
                    f"Substring or regex in {column}",
                )
                if user_text_input:
                    df = df[df[column].str.contains(user_text_input, case=False, na=False)]

    return df
