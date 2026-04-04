def format_currency_columns(df: pd.DataFrame, currency: str = "CLP") -> pd.DataFrame:
    """
    Format all numeric columns (int or float) in a dataframe as currency.
    
    Args:
        df: Input DataFrame
        currency: Currency type, either "CLP" or "USD" (default: "CLP")
    
    Returns:
        DataFrame with numeric columns formatted as currency strings
    
    Examples:
        >>> df = pd.DataFrame({'amount': [1000.5, 2000.75], 'count': [5, 10]})
        >>> format_currency_columns(df, currency="CLP")
        >>> # Returns DataFrame with 'amount' and 'count' formatted as "CLP 1,001", "CLP 2,001", etc.
    """
    df = df.copy()
    
    # Find all numeric columns (int and float)
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    
    if currency.upper() == "CLP":
        # CLP: no decimal places, use comma as thousands separator
        for col in numeric_cols:
            df[col] = df[col].apply(
                lambda x: f"CLP {x:,.0f}" if pd.notna(x) else x
            )
    elif currency.upper() == "USD":
        # USD: 2 decimal places, use comma as thousands separator
        for col in numeric_cols:
            df[col] = df[col].apply(
                lambda x: f"${x:,.2f}" if pd.notna(x) else x
            )
    else:
        raise ValueError(f"Unsupported currency: {currency}. Use 'CLP' or 'USD'.")
    
    return df