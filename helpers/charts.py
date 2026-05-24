"""
Altair chart definitions for the dashboard.
"""
import json
from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st
from helpers.data_transformations.aggregations import get_categories_ranked_by_amount


# ==========================================
# Configuration & Helpers
# ==========================================
def load_budget_colors():
    """Load budget color mappings from JSON file."""
    colors_path = Path(__file__).parent / "constants" / "budget_colors.json"
    with open(colors_path, "r", encoding="utf-8") as f:
        return json.load(f)
    

# ==========================================
# Time-based Charts
# ==========================================
def bar_chart_transactions_by_type(df, period="Month"):

    if period == "Month":
        x_axis = "month:O"
    elif period == "Week":
        x_axis = "week:O"
    else:
        x_axis = "day:O"

    chart = alt.Chart(df).mark_bar().encode(
    x=x_axis,
    y='sum(amount):Q',
    color=alt.Color('type:N', scale=alt.Scale(domain=['Expense', 'Income'], range=['#EF4348', '#28B16A'])),
    xOffset='type:N'
)
    return chart

def render_transactions_tabbed_chart(df, granularity):
    """
    Renders a tabbed chart of transactions based on granularity.
    """
    if granularity == "Month":
        tabs_config = [("Weeks", "Week"), ("Days", "Day"), ("Months", "Month")]
    elif granularity == "Year":
        tabs_config = [("Months", "Month"), ("Weeks", "Week"), ("Days", "Day")]
    else:
        tabs_config = [("Days", "Day"), ("Weeks", "Week"), ("Months", "Month")]

    tabs = st.tabs([t[0] for t in tabs_config])
    for tab, (label, period) in zip(tabs, tabs_config):
        with tab:
            st.altair_chart(bar_chart_transactions_by_type(df, period=period), use_container_width=True)



def chart_expenses_by_period(df, period="Month"):
    """
    Create vertical bar chart for expenses by period (Month or Week).
    
    Args:
        df: DataFrame with 'date' and 'amount' columns
        period: "Month" or "Week"
    """
    df = df.copy()
    
    if period == "Month":
        # Format as YYYY-MM
        df["period"] = df["date"].dt.strftime("%Y-%m")
        title = "Expenses by Month"
        x_title = "Month"
    elif period == "Week":
        # Format as YYYY-WXX (ISO week number)
        df["period"] = df["date"].dt.strftime("%Y-W%V")
        title = "Expenses by Week"
        x_title = "Week"
    else:
        # Default to month
        df["period"] = df["date"].dt.strftime("%Y-%m")
        title = "Expenses by Month"
        x_title = "Month"
    
    # Aggregate by period
    period_data = df.groupby("period")["amount"].sum().reset_index().sort_values("period")
    
    chart = (
        alt.Chart(period_data)
        .mark_bar()
        .encode(
            x=alt.X("period:N", title=x_title, sort="x"),
            y=alt.Y("amount:Q", title="Amount (CLP)", axis=alt.Axis(format="~s")),
            tooltip=["period", alt.Tooltip("amount:Q", format="~s", title="Amount")]
        )
        .properties(
            width="container",
            height=400,
            title=title
        )
    )
    return chart


from helpers.constants.budgets import SORT_ORDER

def chart_expenses_by_budget_month(df):
    """
    Create stacked bar chart for expenses by budget and month.
    Budgets are ordered according to SORT_ORDER in utilities.constants.budgets.
    Args:
        df: DataFrame with 'date', 'budget', and 'amount' columns
    """
    df = df.copy()
    
    # Load budget colors
    budget_colors = load_budget_colors()
    
    # Define budget order based on SORT_ORDER
    # Sort dictionaries by value to get our ordered list
    ordered_budgets = sorted(SORT_ORDER.keys(), key=lambda x: SORT_ORDER[x])
    # Ensure any budgets not in SORT_ORDER are also included at the end
    all_budgets = df["budget"].unique().tolist()
    missing_budgets = sorted([b for b in all_budgets if b not in SORT_ORDER])
    final_order = ordered_budgets + missing_budgets
    
    # Create ordered categorical for budget
    df["budget"] = pd.Categorical(df["budget"], categories=final_order, ordered=True)
    
    # Sort by date and budget
    df = df.sort_values(["date", "budget"])
    
    # Build color scale domain and range from budget colors
    domain = final_order
    range_colors = [budget_colors.get(budget, "#808080") for budget in final_order]
    
    chart = (
        alt.Chart(df)
        .mark_bar(
            cornerRadiusTopLeft=3,
            cornerRadiusTopRight=3
        )
        .encode(
            x=alt.X("month(date):O", title="Month"),
            y=alt.Y("amount:Q", title="Amount (CLP)", axis=alt.Axis(format="~s")),
            color=alt.Color(
                "budget:N",
                title="Budget",
                scale=alt.Scale(domain=domain, range=range_colors),
                sort=final_order
            ),
            tooltip=[
                alt.Tooltip("month(date):O", title="Month"),
                "budget",
                alt.Tooltip("amount:Q", format="~s", title="Amount")
            ]
        )
        .properties(
            width="container",
            height=400,
            title="Expenses by Budget and Month"
        )
    )
    
    return chart


# ==========================================
# Category & Label Charts
# ==========================================
def bar_chart_by_category(df):
    """
    Create horizontal bar chart for expenses by category.
    
    Args:
        df: DataFrame with 'category' and 'amount_universal_clp' columns
    """
    
    # Get unique items in the dataframe ranked by amount
    items = get_categories_ranked_by_amount(df, column="category")
    
    # Base chart - Swapped to Y axis for horizontal orientation
    base = alt.Chart(df).encode(
        y=alt.Y("category:N", title="Category", sort=items)
    )
    
    # Bar layer - Quantitative value on X axis
    bars = base.mark_bar(
        stroke="slategray",
        strokeWidth=0.5
    ).encode(
        x=alt.X("amount_universal_clp:Q", title="Amount (CLP)", axis=alt.Axis(format="$,.0f")),
        color=alt.Color(
            "category:N",
            legend=None
        ),
        tooltip=["category", alt.Tooltip("amount_universal_clp:Q", format="$,.0f", title="Amount"), "note", "labels", alt.Tooltip("date:T", format="%Y-%m-%d", title="Date")]
    )
    
    # Text layer for total amount at the end of each bar
    text = base.mark_text(
        align='left',
        baseline='middle',
        dx=5,
        fontWeight='bold',
        color='white'
    ).encode(
        x=alt.X("sum(amount_universal_clp):Q", stack=None),
        text=alt.Text("sum(amount_universal_clp):Q", format="$,.0f")
    )
    
    return (bars + text).properties(
        width="container",
        height=500,
    )


def bar_chart_by_label(df):
    """
    Create horizontal bar chart for expenses by label at the transaction level.
    Labels column may contain comma-separated values; each label is counted individually.
    Bars are segmented per transaction, colored by category.

    Args:
        df: DataFrame with 'labels', 'category', 'note', 'amount_universal_clp', 'date' columns
    """
    from helpers.constants.category_and_label_colors import CATEGORY_COLORS

    df = df.copy()
    df["labels"] = df["labels"].fillna("").astype(str)

    # Explode comma-separated labels into individual rows
    df["labels"] = df["labels"].str.split(",")
    df = df.explode("labels")
    df["labels"] = df["labels"].str.strip()
    df = df[df["labels"] != ""]

    if df.empty:
        return alt.Chart(pd.DataFrame({"labels": [], "amount_universal_clp": []})).mark_bar()

    items = get_categories_ranked_by_amount(df, column="labels")

    unique_categories = df["category"].dropna().unique().tolist()
    cat_range_colors = [CATEGORY_COLORS.get(cat, "#808080") for cat in unique_categories]

    base = alt.Chart(df).encode(
        y=alt.Y("labels:N", title="Label", sort=items)
    )

    bars = base.mark_bar(
        stroke="slategray",
        strokeWidth=0.5
    ).encode(
        x=alt.X("amount_universal_clp:Q", title="Amount (CLP)", axis=alt.Axis(format="$,.0f")),
        color=alt.Color(
            "category:N",
            scale=alt.Scale(domain=unique_categories, range=cat_range_colors),
            legend=None
        ),
        tooltip=[
            "labels",
            "category",
            alt.Tooltip("amount_universal_clp:Q", format="$,.0f", title="Amount"),
            "note",
            alt.Tooltip("date:T", format="%Y-%m-%d", title="Date"),
        ]
    )

    text = base.mark_text(
        align='left',
        baseline='middle',
        dx=5,
        fontWeight='bold',
        color='white'
    ).encode(
        x=alt.X("sum(amount_universal_clp):Q", stack=None),
        text=alt.Text("sum(amount_universal_clp):Q", format="$,.0f")
    )

    return (bars + text).properties(
        width="container",
        height=500,
    )


def bar_chart_by_budget(df):
    """
    Create horizontal bar chart for expenses by budget.
    
    Args:
        df: DataFrame with 'budget' and 'amount_universal_clp' columns
    """
    
    # Define budget order based on SORT_ORDER in utilities.constants.budgets
    ordered_budgets = sorted(SORT_ORDER.keys(), key=lambda x: SORT_ORDER[x])
    # Ensure any budgets not in SORT_ORDER are also included at the end
    all_budgets = df["budget"].unique().tolist()
    missing_budgets = sorted([b for b in all_budgets if b not in SORT_ORDER])
    final_order = ordered_budgets + missing_budgets
    
    from helpers.constants.category_and_label_colors import CATEGORY_COLORS
    
    # Get unique categories for color scale
    unique_categories = df["category"].dropna().unique().tolist()
    cat_range_colors = [CATEGORY_COLORS.get(cat, "#808080") for cat in unique_categories]
    
    # Determine tick values with steps of 50,000
    max_amount = df.groupby('budget')['amount_universal_clp'].sum().max() if not df.empty else 0
    max_amount = 0 if pd.isna(max_amount) else int(max_amount)
    tick_values = list(range(0, max_amount + 50000, 50000))
    
    # Base chart
    base = alt.Chart(df).encode(
        y=alt.Y("budget:N", title="Budget", sort=final_order)
    )
    
    # Bar layer
    bars = base.mark_bar(
        stroke="slategray",
        strokeWidth=0.5
    ).encode(
        x=alt.X("amount_universal_clp:Q", title="Amount (CLP)", axis=alt.Axis(format="$,.0f", values=tick_values)),
        color=alt.Color(
            "category:N",
            scale=alt.Scale(domain=unique_categories, range=cat_range_colors),
            legend=None
        ),
        tooltip=["budget", "category", alt.Tooltip("amount_universal_clp:Q", format="$,.0f", title="Amount"), "note", "labels", alt.Tooltip("date:T", format="%Y-%m-%d", title="Date")]
    )
    
    # Text layer
    text = base.mark_text(
        align='left',
        baseline='middle',
        dx=5,
        fontWeight='bold',
        color='white'
    ).encode(
        x=alt.X("sum(amount_universal_clp):Q", stack=None),
        text=alt.Text("sum(amount_universal_clp):Q", format="$,.0f")
    )
    
    return (bars + text).properties(
        width="container",
        height=300,
    )


def budget_subtotals_table(df):
    """
    Renders a Streamlit table with subtotals by budget and a grand total.
    """
    if df.empty:
        st.caption("No data available.")
        return

    # Calculate subtotals
    subtotals = df.groupby("budget", as_index=False)["amount_universal_clp"].sum()
    
    # Sort according to SORT_ORDER
    subtotals["sort_key"] = subtotals["budget"].map(lambda x: SORT_ORDER.get(x, 999))
    subtotals = subtotals.sort_values("sort_key").drop(columns=["sort_key"])
    
    # Calculate grand total
    grand_total = subtotals["amount_universal_clp"].sum()
    
    # Add grand total row
    total_row = pd.DataFrame([{"budget": "Grand Total", "amount_universal_clp": grand_total}])
    final_df = pd.concat([subtotals, total_row], ignore_index=True)
    
    # Format the amount column
    final_df["amount_universal_clp"] = final_df["amount_universal_clp"].apply(lambda x: f"${x:,.0f}")
    
    # Set index to Budget to hide the numerical index in the table
    final_df = final_df.set_index("budget")
    final_df.index.name = "Budget"
    final_df = final_df.rename(columns={"amount_universal_clp": "Amount (CLP)"})
    
    st.table(final_df)


def chart_top_expenses_by_label(df):
    """
    Create horizontal bar chart for top expenses by label.
    
    Args:
        df: DataFrame with 'label', 'amount', and 'category' columns
    """
    from helpers.constants.category_and_label_colors import CATEGORY_COLORS

    df = df.copy()

    # Format amount for text label
    df["amount_text"] = df["amount"].apply(lambda x: f"${x:,.0f}")

    # Get unique categories in the dataframe
    categories = df["category"].unique().tolist() if "category" in df.columns else []

    # Create domain and range for color scale
    domain = categories
    range_colors = [CATEGORY_COLORS.get(cat, "#808080") for cat in categories]
    
    # Base chart with bars
    encode_dict = {
        "x": alt.X("amount:Q", title="", axis=None),
        "y": alt.Y("label:N", title="Label", sort="-x"),
        "tooltip": [
            "label",
            alt.Tooltip("amount:Q", format="~s", title="Amount"),
            "category"
        ]
    }
    
    # Add color encoding if category column exists
    if "category" in df.columns and domain:
        encode_dict["color"] = alt.Color(
            "category:N",
            scale=alt.Scale(domain=domain, range=range_colors),
            legend=alt.Legend(title="Category")
        )
    else:
        encode_dict["color"] = alt.value("#808080")
        encode_dict["tooltip"] = [
            "label",
            alt.Tooltip("amount:Q", format="~s", title="Amount")
        ]
    
    bars = (
        alt.Chart(df)
        .mark_bar()
        .encode(**encode_dict)
    )
    
    # Text labels at the end of bars
    text = (
        alt.Chart(df)
        .mark_text(align="left", baseline="middle", dx=3)
        .encode(
            x=alt.X("amount:Q", title=""),
            y=alt.Y("label:N", sort="-x"),
            text="amount_text:N"
        )
    )
    
    chart = (
        (bars + text)
        .properties(
                width="container",
                height=400,
                title="Expenses by Label"
            )
        )
    return chart


# ==========================================
# Transaction Charts
# ==========================================
def chart_top_transactions(df):
    """
    Create horizontal bar chart for top transactions.
    
    Args:
        df: DataFrame with transaction details including 'category' and 'note'
    """
    # Create a label for the bars (category + note if available)
    df = df.copy()
    df["label"] = df.apply(
        lambda row: f"{row['category']}" + (f" - {row['note']}" if pd.notna(row['note']) and row['note'] else ""),
        axis=1
    )
    
    chart = (
        alt.Chart(df)
        .mark_bar()
        .encode(
            x=alt.X("amount:Q", title="Amount (CLP)", axis=alt.Axis(format="~s")),
            y=alt.Y("label:N", title="Transaction", sort="-x"),
            color=alt.Color("category:N", legend=alt.Legend(title="Category")),
            tooltip=[
                "label",
                alt.Tooltip("amount:Q", format="~s", title="Amount"),
                alt.Tooltip("date:T", format="%Y-%m-%d", title="Date")
            ]
        )
        .properties(
            width="container",
            height=400,
            title="Top 10 Transactions"
        )
    )
    return chart
