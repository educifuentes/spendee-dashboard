"""
Altair chart definitions for the dashboard.
"""
import json
from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st
from utilities.transforms import get_categories_ranked_by_amount


# ==========================================
# Configuration & Helpers
# ==========================================
def load_category_colors():
    """Load category color mappings from SCSS file."""
    colors_path = Path(__file__).parent.parent / "utilities" / "constants" / "category_colors.scss"
    colors = {}
    
    if not colors_path.exists():
        return colors

    with open(colors_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line.startswith("$") and ":" in line:
                key, value = line.split(":", 1)
                # Convert $variable-name to "Variable Name"
                # e.g. $personal-care -> Personal Care
                category = key.strip().lstrip("$").replace("-", " ").title()
                color = value.strip().rstrip(";")
                colors[category] = color
    return colors


def load_budget_colors():
    """Load budget color mappings from JSON file."""
    colors_path = Path(__file__).parent.parent / "utilities" / "constants" / "budget_colors.json"
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


def chart_expenses_by_budget_month(df):
    """
    Create stacked bar chart for expenses by budget and month.
    Budgets are ordered: "Gastos fijos" first, then "Chao culpa", then others.
    Args:
        df: DataFrame with 'date', 'budget', and 'amount' columns
    """
    df = df.copy()
    
    # Load budget colors
    budget_colors = load_budget_colors()
    
    # Define budget order: "Gastos fijos" first, then "Chao culpa", then others
    budget_order = ["Gastos fijos", "Chao culpa"]
    all_budgets = df["budget"].unique().tolist()
    other_budgets = [b for b in all_budgets if b not in budget_order]
    ordered_budgets = budget_order + sorted(other_budgets)
    
    # Create ordered categorical for budget
    df["budget"] = pd.Categorical(df["budget"], categories=ordered_budgets, ordered=True)
    
    # Sort by date and budget
    df = df.sort_values(["date", "budget"])
    
    # Build color scale domain and range from budget colors
    domain = ordered_budgets
    range_colors = [budget_colors.get(budget, "#808080") for budget in ordered_budgets]
    
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
                sort=ordered_budgets
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
    Create vertical bar chart for expenses by category.
    
    Args:
        df: DataFrame with 'category' and 'amount' columns
    """
    
    # Get unique categories in the dataframe
    categories = get_categories_ranked_by_amount(df)
    
    chart = (
        alt.Chart(df)
        .mark_bar()
        .encode(
            x=alt.X("category:N", title="Category", sort=categories),
            y=alt.Y("amount_universal_clp:Q", title="Amount (CLP)", axis=alt.Axis(format="~s")),
            color=alt.Color(
                "category:N",
                legend=None
            ),
            tooltip=["category", alt.Tooltip("amount_universal_clp:Q", format="~s", title="Amount"), "note", "labels"]
        )
        .properties(
            width="container",
            height=400,
        )
    )
    return chart


def chart_top_expenses_by_label(df):
    """
    Create horizontal bar chart for top expenses by label.
    
    Args:
        df: DataFrame with 'label', 'amount', and 'category' columns
    """
    df = df.copy()
    
    # Format amount for text label
    df["amount_text"] = df["amount"].apply(lambda x: f"${x:,.0f}")
    
    # Load category colors
    category_colors = load_category_colors()
    
    # Get unique categories in the dataframe
    categories = df["category"].unique().tolist() if "category" in df.columns else []
    
    # Create domain and range for color scale
    domain = categories
    range_colors = [category_colors.get(cat, "#808080") for cat in categories]  # Default to gray if not found
    
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
