"""
Altair chart definitions for the dashboard.
"""
import json
from pathlib import Path

import altair as alt
import pandas as pd


def load_category_colors():
    """Load category color mappings from JSON file."""
    colors_path = Path(__file__).parent.parent / "constants" / "category_color.json"
    with open(colors_path, "r", encoding="utf-8") as f:
        return json.load(f)


def chart_expenses_by_category(df):
    """
    Create vertical bar chart for expenses by category.
    
    Args:
        df: DataFrame with 'category' and 'amount' columns
    """
    # Load category colors
    category_colors = load_category_colors()
    
    # Get unique categories in the dataframe
    categories = df["category"].unique().tolist()
    
    # Create domain and range for color scale
    domain = categories
    range_colors = [category_colors.get(cat, "#808080") for cat in categories]  # Default to gray if not found
    
    chart = (
        alt.Chart(df)
        .mark_bar()
        .encode(
            x=alt.X("category:N", title="Category", sort="-y"),
            y=alt.Y("amount:Q", title="Amount (CLP)", axis=alt.Axis(format="~s")),
            color=alt.Color(
                "category:N",
                scale=alt.Scale(domain=domain, range=range_colors),
                legend=None
            ),
            tooltip=["category", alt.Tooltip("amount:Q", format="~s", title="Amount")]
        )
        .properties(
            width="container",
            height=400,
            title="Expenses by Category (Selected Period)"
        )
    )
    return chart


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
            title="Top 10 Transactions (Current Month)"
        )
    )
    return chart

