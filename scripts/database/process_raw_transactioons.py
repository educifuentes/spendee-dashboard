#!/usr/bin/env python3
"""
process_raw_transactioons.py
────────────────────────────
Pipeline: raw Spendee CSV export → clean DataFrame ready for SQLite.

Runs the same transformations as the model layer in this exact order:
  1. STG  – rename columns, parse dates          (_stg_spendee__transactions)
  2. INT  – period cols, universal amount, budget (_int_spendee__transactions / 2_intermediate.py)
  3. FCT  – abs amount, drop author, record_hash  (_fct_transactions)

Public API
----------
process_raw_spendee_csv(df_raw)  →  pd.DataFrame  (SQLite-ready)

Usage (standalone)
------------------
    cd /path/to/spendee-dashboard
    python scripts/database/process_raw_transactioons.py seeds/uploads/fct_transactions.csv
"""

from __future__ import annotations

import pathlib
import sys

import pandas as pd

# ── bootstrap sys.path so helpers are importable when run as a script ──────
_here = pathlib.Path(__file__).resolve()
_root = _here.parents[2]
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

from helpers.data_transformations.add_record_hash import add_record_hash
from helpers.data_transformations.periods import create_period_columns
from helpers.data_transformations.universal_amount import create_universal_amount
from helpers.constants.budgets import BUDGETS

# ── Column rename: raw Spendee export → internal schema ───────────────────
_RENAME_MAP: dict[str, str] = {
    "Date":          "date",
    "Wallet":        "wallet",
    "Type":          "type",
    "Category name": "category",
    "Amount":        "amount",
    "Currency":      "currency",
    "Note":          "note",
    "Labels":        "labels",
    "Author":        "author",
}

# Columns that must exist after renaming
_REQUIRED_COLS = list(_RENAME_MAP.values())


# ── Step 1: STG ────────────────────────────────────────────────────────────

def _stg(df_raw: pd.DataFrame) -> pd.DataFrame:
    """
    Mirror of _stg_spendee__transactions:
      - rename raw Spendee headers → internal names
      - keep only schema columns
      - parse date
    """
    df = df_raw.copy()

    # Rename whatever matches the map (ignore unknown columns)
    df = df.rename(columns=_RENAME_MAP)

    # Keep only columns we own
    keep = [c for c in _REQUIRED_COLS if c in df.columns]
    df = df[keep]

    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")

    return df


# ── Step 2: INT ────────────────────────────────────────────────────────────

def _int(df: pd.DataFrame) -> pd.DataFrame:
    """
    Mirror of _int_spendee__transactions (rendered by pages/3_dev/2_intermediate.py):
      - add period columns  (day, week, month, year)
      - add amount_universal_clp
      - map budget category
    """
    df = create_period_columns(df)
    df = create_universal_amount(df)
    df["budget"] = df["category"].map(BUDGETS).fillna("Otros")
    return df


# ── Step 3: FCT ────────────────────────────────────────────────────────────

def _fct(df: pd.DataFrame) -> pd.DataFrame:
    """
    Mirror of _fct_transactions:
      - make amount absolute
      - drop author column
      - add record_hash (dedup key used by SQLite)
    """
    df["amount"] = df["amount"].abs()

    if "author" in df.columns:
        df = df.drop(columns=["author"])

    # Hash on the core identity columns (same as what was seeded)
    hash_cols = ["date", "wallet", "type", "category", "amount", "currency", "note", "labels"]
    hash_cols = [c for c in hash_cols if c in df.columns]
    df = add_record_hash(df, columns=hash_cols)

    return df


# ── Public pipeline ────────────────────────────────────────────────────────

def process_raw_spendee_csv(df_raw: pd.DataFrame) -> pd.DataFrame:
    """
    Full pipeline: raw Spendee CSV DataFrame → SQLite-ready DataFrame.

    Parameters
    ----------
    df_raw : pd.DataFrame
        DataFrame loaded directly from a Spendee CSV export (raw headers).

    Returns
    -------
    pd.DataFrame
        Cleaned, enriched DataFrame whose schema matches the ``stg_transaction``
        SQLite table (plus computed columns added by INT/FCT layers).
    """
    df = _stg(df_raw)   # 1. rename + parse
    df = _int(df)       # 2. period cols, universal amount, budget
    df = _fct(df)       # 3. abs amount, drop author, record_hash
    return df


# ── CLI smoke-test ─────────────────────────────────────────────────────────

if __name__ == "__main__":
    csv_path = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else (
        _root / "seeds" / "uploads" / "fct_transactions.csv"
    )

    print(f"Reading {csv_path} ...")
    raw = pd.read_csv(csv_path)
    print(f"  Raw shape : {raw.shape}")

    clean = process_raw_spendee_csv(raw)
    print(f"  Clean shape: {clean.shape}")
    print(f"  Columns    : {list(clean.columns)}")
    print(clean.head(5).to_string())