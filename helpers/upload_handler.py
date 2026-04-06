"""
helpers/upload_handler.py
─────────────────────────
Encapsulates the full Spendee CSV upload flow:
  1. Parse & process uploaded files (STG → INT → FCT pipeline)
  2. Dedup against the SQLite database
  3. Preview new records
  4. Insert into SQLite and sync to GCS

Public API
----------
render_upload_ui()   — call from any Streamlit page
"""

from __future__ import annotations

import pandas as pd
import streamlit as st

from scripts.database.process_raw_transactioons import process_raw_spendee_csv
from helpers.sqlite_loader import get_latest_transaction_date, insert_into_sqlite


def _process_files(uploaded_files) -> pd.DataFrame:
    """Read & pipeline-process all uploaded CSV files into one DataFrame."""
    df_list = []
    for f in uploaded_files:
        f.seek(0)
        raw = pd.read_csv(f)
        df_list.append(process_raw_spendee_csv(raw))

    if not df_list:
        return pd.DataFrame()

    return pd.concat(df_list, ignore_index=True)


def _filter_new_transactions(df: pd.DataFrame) -> tuple[pd.DataFrame, str | None]:
    """
    Compare against the latest SQLite date and return only new rows.

    Returns
    -------
    (new_rows, info_message)
    """
    latest_date = get_latest_transaction_date()

    if latest_date is None:
        return df.copy(), "No existing transactions found — all rows will be inserted."

    # Normalise timezone before comparison
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    if df["date"].dt.tz is not None:
        df["date"] = df["date"].dt.tz_localize(None)

    new_rows = df[df["date"] > latest_date].copy()
    msg = f"Latest transaction in database: **{latest_date.date()}**"
    return new_rows, msg


def render_upload_ui() -> None:
    """
    Full Streamlit upload UI.
    Drop this into any page with a single call:

        from helpers.upload_handler import render_upload_ui
        render_upload_ui()
    """
    st.write("Go to Spendee App → Settings → Advanced → Export")
    st.write("You can upload multiple CSV files at once.")

    uploaded_files = st.file_uploader(
        "Choose CSV files",
        type="csv",
        accept_multiple_files=True,
        key="csv_uploader",
    )

    if not uploaded_files:
        return

    try:
        # ── 1. Process ──────────────────────────────────────────────────────
        with st.spinner("Processing files through STG → INT → FCT pipeline..."):
            df = _process_files(uploaded_files)

        if df.empty:
            st.error("No data found in the uploaded files.")
            return

        st.metric("Total rows processed", len(df))

        # ── 2. Dedup ────────────────────────────────────────────────────────
        with st.spinner("Checking latest transaction in SQLite..."):
            new_transactions, info_msg = _filter_new_transactions(df)

        if info_msg:
            st.write(info_msg)

        st.metric("New records to upload", len(new_transactions))

        # ── 3. Nothing new ──────────────────────────────────────────────────
        if new_transactions.empty:
            st.info("No new records to upload. Everything is already in the database.")
            if st.button("Start over"):
                st.rerun()
            return

        # ── 4. Preview ──────────────────────────────────────────────────────
        st.subheader("Preview (first 20 rows)")
        st.dataframe(new_transactions.head(20), use_container_width=True)

        # ── 5. Confirm / cancel ─────────────────────────────────────────────
        col1, col2 = st.columns([1, 5])

        with col1:
            if st.button("Upload to Database", type="primary"):
                with st.spinner("Inserting into SQLite and syncing to GCS..."):
                    rows_inserted = insert_into_sqlite(new_transactions, upload_to_gcs=True)
                st.success(f"✅ Successfully uploaded **{rows_inserted}** new records!")
                st.cache_data.clear()

        with col2:
            if st.button("Cancel"):
                st.rerun()

    except Exception as e:
        st.error(f"Error processing files: {e}")
        if st.button("Try again"):
            st.rerun()
