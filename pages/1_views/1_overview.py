import streamlit as st
import pandas as pd

from models.exposures.spendee._exp_transactions import exp_transactions
from models.metrics.spendee._metric_expenses import metric_expenses
from helpers.constants.category_and_label_colors import CATEGORY_COLORS, EXPENSES_CATEGORY_COLORS, INCOME_CATEGORY_COLORS
from helpers.ui_components.category_grid import render_category_grid

from helpers.charts import (
    bar_chart_by_category,
    bar_chart_by_label,
    bar_chart_by_budget,
    budget_subtotals_table,
    render_transactions_tabbed_chart
)
from helpers.misc import setup_period_selection, get_wallet_options
from helpers.data_transformations.filtering import filter_by_date_range
from helpers.data_transformations.aggregations import (
    get_current_month_expenses,
    get_current_month_income,
    get_last_month_expenses,
    get_last_month_income,
    get_transactions_by_category_sorted,
    get_transactions_by_labels_sorted
)
from helpers.data_transformations.periods import (
    get_available_periods,
    get_period_dates
)

# 1. Load Data
fct_transactions_df = exp_transactions()

# 2. Header & Metrics
st.title(":material/paid: Gastos Spendee")
st.caption(f"Rango de datos: {fct_transactions_df['date'].min().date()} a {fct_transactions_df['date'].max().date()}")


# st.subheader("Current Month Summary")
# m1, m2, m3, m4 = st.columns(4)

# # MTD Comparison for primary metric
# curr_mtd, last_mtd, pct_change = metric_expenses(fct_transactions_df)
# # Keep other monthly totals for context
# curr_exp = get_current_month_expenses(fct_transactions_df)
# last_exp = get_last_month_expenses(fct_transactions_df)

# m1.metric(
#     "MTD Expenses vs Last Month", 
#     f"${curr_mtd:,.0f}", 
#     delta=f"{pct_change:+.1f}%",
#     help=f"Compared to ${last_mtd:,.0f} spent by this day last month."
# )
# m2.metric("Gastos Mes Actual", f"${curr_exp:,.0f}")
# m3.metric(
#     "Ingreso Mes Actual", 
#     f"${get_current_month_income(fct_transactions_df):,.0f}",
#     delta=f"${get_current_month_income(fct_transactions_df, wallet='Pasivos'):,.0f} Pasivos",
#     delta_color="off",
#     delta_arrow="off"
# )
# m4.metric(
#     "Ingreso Mes Pasado", 
#     f"${get_last_month_income(fct_transactions_df):,.0f}",
#     delta=f"${get_last_month_income(fct_transactions_df, wallet='Pasivos'):,.0f} Pasivos",
#     delta_color="off",
#     delta_arrow="off"
# )

# st.divider()

# 3. Filters & Period Selection
granularity, selected_label, period_options, period_values, default_index = setup_period_selection(
    fct_transactions_df, get_available_periods
)

st.title(f"{selected_label}")

c1, c2, c3 = st.columns(3)
with c1:
    granularity = st.selectbox("Período", ["Month", "Week", "Year"], format_func=lambda x: {"Month": "Mes", "Week": "Semana", "Year": "Año"}[x], index=0, key="granularity")
with c2:
    selected_label = st.selectbox(granularity, period_options, index=default_index, key="selected_period_label")
with c3:
    wallet_options = get_wallet_options(fct_transactions_df, include_all=False)
    default_wallet = [w for w in wallet_options if "Main CLP" in w]
    selected_wallets = st.multiselect("Billeteras", wallet_options, default=default_wallet)

start_date, end_date = get_period_dates(granularity, period_values[selected_label])

# Helper for inline filtering based on current selection
def get_filtered_data(df, type_filter=None):
    data = filter_by_date_range(df, start_date, end_date)
    if selected_wallets:
        data = data[data["wallet"].isin(selected_wallets)]
    if type_filter:
        data = data[data["type"] == type_filter]
    return data

st.markdown(f"### {end_date.strftime('%B %Y')}")

sel_income = get_filtered_data(fct_transactions_df, "Income")["amount"].sum()
sel_expense = get_filtered_data(fct_transactions_df, "Expense")["amount"].sum()

sc1, sc2, sc3 = st.columns(3)
sc1.metric("Ingreso Período Seleccionado", f"${sel_income:,.0f}")
sc2.metric("Gastos Período Seleccionado", f"${sel_expense:,.0f}")
sc3.metric("Neto", f"${sel_income - sel_expense:,.0f}")


# 4. Visualizations
st.subheader("Por Categoría")
t1, t2 = st.tabs(["Gastos", "Ingresos"])

with t1:
    st.altair_chart(bar_chart_by_category(get_filtered_data(fct_transactions_df, "Expense")), use_container_width=True)
with t2:
    st.altair_chart(bar_chart_by_category(get_filtered_data(fct_transactions_df, "Income")), use_container_width=True)

st.subheader("Por Etiqueta")
st.altair_chart(bar_chart_by_label(get_filtered_data(fct_transactions_df, "Expense")), use_container_width=True)

st.divider()

st.subheader("Por Presupuesto")
st.altair_chart(bar_chart_by_budget(get_filtered_data(fct_transactions_df, "Expense")), use_container_width=True)

# budget total table
budget_subtotals_table(get_filtered_data(fct_transactions_df, "Expense"))
st.divider()

render_category_grid(EXPENSES_CATEGORY_COLORS, INCOME_CATEGORY_COLORS)

st.divider()
# 5. Transactions
st.subheader("Transacciones")

tab_exp, tab_inc = st.tabs(["Gastos", "Ingresos"])

with tab_exp:
    exp_data = get_filtered_data(fct_transactions_df, "Expense")
    
    col_cat_e, col_lbl_e = st.columns(2)
    with col_cat_e:
        exp_categories = sorted(exp_data["category"].dropna().unique())
        sel_cat_e = st.multiselect("Filtrar por Categoría", exp_categories, key="cat_exp")
    
    with col_lbl_e:
        exp_labels = sorted(exp_data["labels"].dropna().astype(str).unique())
        sel_lbl_e = st.multiselect("Filtrar por Etiqueta", exp_labels, key="lbl_exp")
    
    filt_exp = exp_data.copy()
    if sel_cat_e:
        filt_exp = filt_exp[filt_exp["category"].isin(sel_cat_e)]
    if sel_lbl_e:
        filt_exp = filt_exp[filt_exp["labels"].astype(str).isin(sel_lbl_e)]
    
    st.dataframe(
        filt_exp[["note", "category", "labels", "amount", "date"]].sort_values(by="date", ascending=False),
        use_container_width=True,
        hide_index=True,
        column_config={
            "date": st.column_config.DateColumn("Fecha", format="YYYY-MM-DD"),
            "category": st.column_config.MultiselectColumn("Categoría", options=exp_categories, color=[CATEGORY_COLORS.get(c, "auto") for c in exp_categories]),
            "labels": st.column_config.MultiselectColumn("Etiquetas", options=exp_labels),
            "amount": st.column_config.NumberColumn("Monto", format="$%d")
        }
    )
    st.write(f"**Subtotal:** ${filt_exp['amount'].sum():,.0f}")

with tab_inc:
    inc_data = get_filtered_data(fct_transactions_df, "Income")
    
    col_cat_i, col_lbl_i = st.columns(2)
    with col_cat_i:
        inc_categories = sorted(inc_data["category"].dropna().unique())
        sel_cat_i = st.multiselect("Filtrar por Categoría", inc_categories, key="cat_inc")
    
    with col_lbl_i:
        inc_labels = sorted(inc_data["labels"].dropna().astype(str).unique())
        sel_lbl_i = st.multiselect("Filtrar por Etiqueta", inc_labels, key="lbl_inc")
    
    filt_inc = inc_data.copy()
    if sel_cat_i:
        filt_inc = filt_inc[filt_inc["category"].isin(sel_cat_i)]
    if sel_lbl_i:
        filt_inc = filt_inc[filt_inc["labels"].astype(str).isin(sel_lbl_i)]
    
    st.dataframe(
        filt_inc[["note", "category", "labels", "amount", "date"]].sort_values(by="date", ascending=False),
        use_container_width=True,
        hide_index=True,
        column_config={
            "date": st.column_config.DateColumn("Fecha", format="YYYY-MM-DD"),
            "category": st.column_config.MultiselectColumn("Categoría", options=inc_categories, color=[CATEGORY_COLORS.get(c, "auto") for c in inc_categories]),
            "labels": st.column_config.MultiselectColumn("Etiquetas", options=inc_labels),
            "amount": st.column_config.NumberColumn("Monto", format="$%d")
        }
    )
    st.write(f"**Subtotal:** ${filt_inc['amount'].sum():,.0f}")







