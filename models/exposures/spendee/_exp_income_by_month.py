import pandas as pd
from models.exposures.spendee._exp_transactions import exp_transactions

def exp_income_by_month():
    """
    Model that filters transactions by 'Income' and aggregates the sum of amounts by month.
    """
    df = exp_transactions()
    
    # Filter by income
    df_income = df[df['type'].str.lower() == 'income']
    
    # Aggregate amount by month
    # We will sum both amount and amount_universal_clp
    grouped = df_income.groupby('month', as_index=False)[['amount', 'amount_universal_clp']].sum()
    
    # Sort chronologically (assuming month is e.g. YYYY-MM)
    grouped = grouped.sort_values('month', ascending=False).reset_index(drop=True)
    
    return grouped
