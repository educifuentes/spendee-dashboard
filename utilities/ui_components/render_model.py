import streamlit as st

def render_model_ui(df, source_name=None, table_name=None):
    """
    Renders a standard UI component for a data model summary.
    Includes shape, columns, and the dataframe.
    Optionally fetches and displays description from YAML config.
    """
    # if source_name and table_name:
    #     config = get_table_config(source_name=source_name, table_name=table_name)
    #     if config and config.get("description"):
    #         st.markdown(config.get("description"))

    # st.markdown(f"Source: `{source_name}.{table_name}`")
    st.write(df.shape)
    st.code(df.columns.tolist())
    # Format dtypes as a single line: col1: type1 | col2: type2
    dtypes_str = " | ".join([f"{col}: {dtype}" for col, dtype in df.dtypes.items()])
    st.code(dtypes_str)
    st.dataframe(df)
    st.divider()