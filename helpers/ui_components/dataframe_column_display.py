import streamlit as st
import pandas as pd

def dataframe_column_display(
    df: pd.DataFrame, 
    currency_cols: list = None, 
    date_cols: list = None, 
    selectbox_cols: list = None, 
    multiselect_cols: list = None,
    hide_index: bool = True,
    use_container_width: bool = True
):
    """
    Renders a Streamlit dataframe with custom column configurations.
    
    Args:
        df: The dataframe to display.
        currency_cols: List of column names to format as currency.
        date_cols: List of column names to format as dates.
        selectbox_cols: List of column names to display as SelectboxColumn.
        multiselect_cols: List of column names to display as MultiselectColumn.
    """
    column_config = {}
    
    # helper to get unique options
    def get_options(col_name):
        if col_name in df.columns:
            return sorted([str(x) for x in df[col_name].unique() if pd.notna(x)])
        return []

    # 1. Currency Formatting
    if currency_cols:
        for col in currency_cols:
            if col in df.columns:
                column_config[col] = st.column_config.NumberColumn(
                    col.replace("_", " ").title(),
                    format="$%,.0f"
                )

    # 2. Date Formatting
    if date_cols:
        for col in date_cols:
            if col in df.columns:
                column_config[col] = st.column_config.DateColumn(
                    col.replace("_", " ").title(),
                    format="DD/MM/YYYY"
                )

    # 3. Selectbox Columns
    if selectbox_cols:
        for col in selectbox_cols:
            if col in df.columns:
                column_config[col] = st.column_config.SelectboxColumn(
                    col.replace("_", " ").title(),
                    options=get_options(col),
                    required=True
                )

    # 4. Multiselect Columns
    if multiselect_cols:
        for col in multiselect_cols:
            if col in df.columns:
                column_config[col] = st.column_config.MultiselectColumn(
                    col.replace("_", " ").title(),
                    options=get_options(col),
                    required=True
                )

    st.dataframe(
        df,
        column_config=column_config,
        hide_index=hide_index,
        use_container_width=use_container_width
    )
