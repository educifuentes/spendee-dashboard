import streamlit as st
from src.data_preparation import load_transactions
from utilities.ui_components.column_formatting import format_currency_columns

df = load_transactions()

excluded_categories = ["Mortgage"]    
expenses_df = df[(df["type"] == "Expense") & (~df["category"].isin(excluded_categories))]

st.title(":material/inventory_2: Transactions Report")

st.subheader("Top 40 Expenses")

top_50 = expenses_df.sort_values(by="amount_universal_clp", ascending=False).head(40)

selected_columns = [
    "date",
    "amount",
    "currency",
    "amount_universal_clp",
    "category",
    "note",
    "labels"
]

st.dataframe(format_currency_columns(top_50[selected_columns], "CLP"), width='stretch', height="content")

# Category filter
# all_categories = sorted(df["category"].unique())
# selected_categories = st.sidebar.multiselect(
#     "Category",
#     options=all_categories,
#     default=[],
#     width=200
# )

# # Label filter
# all_labels = set()
# for labels_str in df["labels"].dropna():
#     if labels_str:
#         all_labels.update([l.strip() for l in str(labels_str).split(",")])
# all_labels = sorted([l for l in all_labels if l])

# selected_labels = st.sidebar.multiselect(
#     "Label",
#     options=all_labels,
#     default=[],
#     width=200
# )

# st.write("In Progress...")