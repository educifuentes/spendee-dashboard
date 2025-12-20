"""
Altair chart definitions for the dashboard.
"""
import altair as alt
import pandas as pd


def chart_expenses_by_category(df):
    """
    Create vertical bar chart for expenses by category.
    
    Args:
        df: DataFrame with 'category' and 'amount' columns
    """
    chart = (
        alt.Chart(df)
        .mark_bar()
        .encode(
            x=alt.X("category:N", title="Category", sort="-y"),
            y=alt.Y("amount:Q", title="Amount (CLP)", axis=alt.Axis(format="~s")),
            color=alt.Color("category:N", legend=None),
            tooltip=["category", alt.Tooltip("amount:Q", format="~s", title="Amount")]
        )
        .properties(
            width="container",
            height=400,
            title="Expenses by Category (Selected Period)"
        )
    )
    return chart


def chart_expenses_by_month(df):
    """
    Create vertical bar chart for expenses by month.
    
    Args:
        df: DataFrame with 'month_name' and 'amount' columns
    """
    chart = (
        alt.Chart(df)
        .mark_bar()
        .encode(
            x=alt.X("month_name:N", title="Month", sort="x"),
            y=alt.Y("amount:Q", title="Amount (CLP)", axis=alt.Axis(format="~s")),
            color=alt.Color("amount:Q", scale=alt.Scale(scheme="blues"), legend=None),
            tooltip=["month_name", alt.Tooltip("amount:Q", format="~s", title="Amount")]
        )
        .properties(
            width="container",
            height=400,
            title="Expenses by Month (Current Year)"
        )
    )
    return chart


def chart_top_transactions(df):
    """
    Create horizontal bar chart for top transactions.
    
    Args:
        df: DataFrame with transaction details including 'category' and 'amount'
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

