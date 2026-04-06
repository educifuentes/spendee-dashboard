import pandas as pd

from models.staging.spendee._stg_spendee__main_clp import stg_spendee__main_clp
from models.staging.spendee._stg_spendee__unfcu import stg_spendee__unfcu
from models.staging.spendee._stg_spendee__pasivos import stg_spendee__pasivos
from models.staging.spendee._stg_spendee__savings import stg_spendee__savings

from helpers.constants.budgets import BUDGETS
from helpers.data_transformations.periods import create_period_columns
from helpers.data_transformations.universal_amount import create_universal_amount

def int_spendee__transactions():
    """
    Intermediate model that concatenates all Spendee staging models and applies enrichment.
    """
    # 1. Concatenate all staging sources
    df_main = stg_spendee__main_clp()
    df_unfcu = stg_spendee__unfcu()
    df_pasivos = stg_spendee__pasivos()
    df_savings = stg_spendee__savings()
    
    df = pd.concat([df_main, df_unfcu, df_pasivos, df_savings], ignore_index=True)

    # 2. Add enrichment columns
    df = create_period_columns(df)
    df = create_universal_amount(df)

    # 3. Enrich with budget category mapping
    df["budget"] = df["category"].map(BUDGETS).fillna("Otros")
    
    # 4. Transform amount to absolute
    df["amount"] = df["amount"].abs()

    # 5. Drop author column (not needed for analysis)
    if "author" in df.columns:
        df = df.drop(columns=["author"])
    
    # 6. Reorder columns: place amount_universal_clp after currency
    cols = df.columns.tolist()
    if "amount_universal_clp" in cols and "currency" in cols:
        cols.remove("amount_universal_clp")
        currency_index = cols.index("currency")
        cols.insert(currency_index + 1, "amount_universal_clp")
        df = df[cols]
        
    return df