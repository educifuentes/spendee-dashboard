import streamlit as st
from src.data_preparation import load_transactions

df = load_transactions()

st.title(":material/inventory_2: Transactions Report")

st.dataframe(df.sort_values(by="date", ascending=False, inplace=True), width='stretch')

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