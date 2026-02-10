import streamlit as st
import pandas as pd
from src.data_preparation import load_transactions


def detect_outliers(df: pd.DataFrame) -> pd.DataFrame:
    """
    Detect outliers in transaction data based on category-specific rules.
    
    Rules are based on reasonable spending limits for each category in CLP:
    - Groceries: max 100,000 (grocery shopping shouldn't exceed this)
    - Restaurant: max 100,000 (even fancy restaurants rarely exceed this per meal)
    - Coffee-Snacks/Snacks & Coffee: max 20,000 (coffee and snacks should be small)
    - Alcohol: max 50,000 (bottle of wine or drinks)
    - Shopping: max 500,000 (discretionary shopping)
    - Transport: max 50,000 (single trip, even expensive taxis)
    - Utilities: max 300,000 (monthly utilities bill)
    - Subscriptions: max 200,000 (monthly subscription)
    - Rent: max 1,500,000 (monthly rent)
    - Insurance: max 500,000 (monthly insurance payment)
    - Healthcare: max 1,000,000 (medical expenses)
    - Pharmacy: max 50,000 (pharmacy purchase)
    - Maintenance: max 500,000 (home/car maintenance)
    - Personal Care: max 200,000 (spa, salon, etc.)
    - Sport: max 200,000 (sport equipment or activities)
    - Activities: max 100,000 (leisure activities)
    - Gifts: max 500,000 (gift expenses)
    - Travel: max 5,000,000 (travel expenses)
    - Acommodation: max 1,000,000 (hotel/accommodation per stay)
    - Flights: max 3,000,000 (flight tickets)
    - Education: max 2,000,000 (education expenses)
    - Tax: max 5,000,000 (tax payments)
    - Investments: max 10,000,000 (investment transactions)
    - Savings: max 10,000,000 (savings transfers)
    - Other: max 500,000 (catch-all category)
    
    Args:
        df: DataFrame with transactions, must have 'category' and 'amount_universal_clp' columns
        
    Returns:
        DataFrame with outlier transactions (includes a 'reason' column explaining why it's an outlier)
    """
    # Define category-specific thresholds (in CLP)
    category_thresholds = {
        "Groceries": 100_000,
        "Restaurant": 100_000,
        "Coffee-Snacks": 20_000,
        "Snacks & Coffee": 20_000,
        "Alcohol": 50_000,
        "Shopping": 500_000,
        "Transport": 50_000,
        "Utilities": 300_000,
        "Subscriptions": 200_000,
        "Rent": 1_500_000,
        "Insurance": 500_000,
        "Healthcare": 1_000_000,
        "Pharmacy ": 50_000,
        "Maintenance ": 500_000,
        "Personal Care": 200_000,
        "Sport": 200_000,
        "Activities": 100_000,
        "Gifts": 500_000,
        "Travel": 5_000_000,
        "Acommodation": 1_000_000,
        "Flights": 3_000_000,
        "Education": 2_000_000,
        "Tax": 5_000_000,
        "Investments": 10_000_000,
        "Savings": 10_000_000,
        "Other": 500_000,
    }
    
    # Filter to expenses only (if type column exists)
    if "type" in df.columns:
        df_expenses = df[df["type"].str.lower() == "expense"].copy()
    else:
        df_expenses = df.copy()
    
    # Check for required columns
    if "category" not in df_expenses.columns or "amount_universal_clp" not in df_expenses.columns:
        raise ValueError("DataFrame must have 'category' and 'amount_universal_clp' columns")
    
    outliers = []
    
    # Check each transaction against its category threshold
    for idx, row in df_expenses.iterrows():
        category = row["category"]
        amount = row["amount_universal_clp"]
        
        # Skip if amount is NaN
        if pd.isna(amount):
            continue
        
        # Get threshold for this category (default to 500,000 if category not found)
        threshold = category_thresholds.get(category, 500_000)
        
        # If amount exceeds threshold, mark as outlier
        if amount > threshold:
            outlier_row = row.copy()
            outlier_row["outlier_reason"] = f"Amount {amount:,.0f} CLP exceeds threshold of {threshold:,.0f} CLP for category '{category}'"
            outlier_row["threshold"] = threshold
            outliers.append(outlier_row)
    
    if outliers:
        outliers_df = pd.DataFrame(outliers)
        # Reorder columns to put outlier_reason and threshold near the end
        cols = [c for c in outliers_df.columns if c not in ["outlier_reason", "threshold"]]
        cols.extend(["outlier_reason", "threshold"])
        outliers_df = outliers_df[cols]
        return outliers_df
    else:
        # Return empty DataFrame with same structure
        return pd.DataFrame(columns=df_expenses.columns.tolist() + ["outlier_reason", "threshold"])


st.title(":material/warning: Data Outliers Detection Tool")
st.write("Detects transactions that exceed reasonable spending limits for each category.")

# Load data
all_transactions = load_transactions()

# Detect outliers
outliers_df = detect_outliers(all_transactions)

if not outliers_df.empty:
    st.subheader(f"⚠️ Found {len(outliers_df)} outlier(s)")
    
    # Summary metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Outliers", len(outliers_df))
    with col2:
        st.metric("Total Outlier Amount", f"{outliers_df['amount_universal_clp'].sum():,.0f} CLP")
    with col3:
        st.metric("Average Outlier Amount", f"{outliers_df['amount_universal_clp'].mean():,.0f} CLP")
    
    # Display outliers
    st.subheader("Outlier Transactions")
    st.dataframe(outliers_df, width='stretch', height="content")
    
    # Breakdown by category
    if "category" in outliers_df.columns:
        st.subheader("Outliers by Category")
        category_summary = outliers_df.groupby("category").agg({
            "amount_universal_clp": ["count", "sum", "mean"]
        }).round(0)
        category_summary.columns = ["Count", "Total Amount", "Average Amount"]

        selected_columns = ["category", "date", "amount_universal_clp", "outlier_reason", "threshold"]
        st.dataframe(category_summary.sort_values("Total Amount", ascending=False)[selected_columns], width='stretch')
else:
    st.success("✅ No outliers detected! All transactions are within reasonable limits for their categories.")