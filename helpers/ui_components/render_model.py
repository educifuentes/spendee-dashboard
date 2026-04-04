import streamlit as st

def render_model_ui(df, table_name=None):
    """
    Renders a standard UI component for a data model summary.
    Includes shape, columns, and the dataframe.
    Optionally fetches and displays description from YAML config.
    """


    with st.expander(f"`{table_name}`"):
        st.code(f"Shape: {df.shape}")
        with st.expander("Columnas"):
            st.code("\n".join(df.columns))
        with st.expander("Data Types"):
            dtypes_str = "\n".join([f"{col}: {dtype}" for col, dtype in df.dtypes.items()])
            st.code(dtypes_str)
        st.dataframe(df)
    st.divider()