import pandas as pd
from models.staging.gsheets._stg_gsheets__ingresos_proyectaods import stg_gsheets__ingresos_proyectados

def int_gsheets__ingresos_proyectados():
    """
    Intermediate model for Ingresos Proyectados.
    Formats dates and currency columns.
    """
    df = stg_gsheets__ingresos_proyectados()
    
    # Format date as pd.datetime
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        
    # Format monto and monto bruto as numeric currency (filling NaN with 0)
    currency_cols = ["monto", "monto bruto"]
    for col in currency_cols:
        if col in df.columns:
            # Ensure it is numeric first
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
            # You can also cast to int if needed: df[col] = df[col].astype(int)
            
    return df
