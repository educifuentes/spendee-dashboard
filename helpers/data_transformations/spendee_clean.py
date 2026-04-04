import pandas as pd
import hashlib
from helpers.constants.budgets import BUDGETS

def load_budgets():
    """Returns the budget category mapping-."""
    return BUDGETS

def _stable_str(x) -> str:
    if pd.isna(x):
        return ""
    return str(x).strip()

def add_spendee_record_hash(df: pd.DataFrame) -> pd.DataFrame:
    """
    Build a deterministic hash from the transaction content.
    This prevents duplicates even when multiple rows share the same date.
    """
    def row_hash(r) -> str:
        parts = [
            _stable_str(r.get("date")),
            _stable_str(r.get("wallet")),
            _stable_str(r.get("type")),
            _stable_str(r.get("category")),
            _stable_str(r.get("amount")),
            _stable_str(r.get("currency")),
            _stable_str(r.get("note", "")),
            _stable_str(r.get("labels", "")),
            _stable_str(r.get("budget", "")),
        ]
        payload = "|".join(parts).encode("utf-8")
        return hashlib.sha256(payload).hexdigest()

    df = df.copy()
    df["record_hash"] = df.apply(row_hash, axis=1)
    return df
