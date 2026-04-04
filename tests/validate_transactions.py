import streamlit as st
import pandas as pd
from datetime import datetime

from helpers.ui_components.icons import ICONS
from helpers.ui_components.editable_dataframe import editable_transactions_dataframe


def validate_transactions(df):
    st.header("Transactions Data Quality Validation")
    
    # Filter by date (2025 onwards)
    if not df.empty and 'date' in df.columns:
        # Convert threshold to match timezone if necessary
        date_threshold = pd.Timestamp("2025-01-01")
        if df['date'].dt.tz is not None:
            date_threshold = date_threshold.tz_localize('UTC')
        
        df = df[df['date'] >= date_threshold]

    total_filas = len(df)
    if total_filas == 0:
        st.warning("No hay transacciones registradas desde 2025.")
        return

    st.write(f"Total registros a validar (2025+): **{total_filas}**")

    # 1. Column Date
    st.markdown("### 1. `date` ")
    
    # Check for Null/NaN dates
    nulos_date = df[df['date'].isna()]
    if not nulos_date.empty:
        st.error(f"{ICONS['close']} Detectadas {len(nulos_date)} transacciones sin fecha")
        editable_transactions_dataframe(nulos_date, key="val_nulos_date")
    else:
        st.success(f"{ICONS['check']} Todas las transacciones tienen fecha")

    # Check for dates prior to 2016
    threshold_date = pd.Timestamp("2016-01-01", tz="UTC")
    naive_threshold = pd.Timestamp("2016-01-01")
    
    # Handle timezone awareness safely
    if df['date'].dt.tz is not None:
        pre_2016 = df[df['date'] < threshold_date]
    else:
        pre_2016 = df[df['date'] < naive_threshold]

    if not pre_2016.empty:
        st.warning(f"{ICONS['warning']} Detectadas {len(pre_2016)} transacciones anteriores a 2016")
        editable_transactions_dataframe(pre_2016.sort_values("date"), key="val_pre_2016")
    else:
        st.success(f"{ICONS['check']} No hay transacciones anteriores a 2016")

    # 2. Column Amount
    st.markdown("### 2. `amount` ")
    
    # Check for Null amounts
    nulos_amount = df[df['amount'].isna()]
    if not nulos_amount.empty:
        st.error(f"{ICONS['close']} Detectadas {len(nulos_amount)} transacciones sin monto")
        editable_transactions_dataframe(nulos_amount, key="val_nulos_amount")
    
    # Check for extreme amounts
    if all(col in df.columns for col in ["amount", "currency", "type", "category", "wallet"]):
        # 2a. Wallet: Main CLP 🇨🇱 (> 500,000 CLP)
        mask_clp = (
            (df['wallet'] == 'Main CLP 🇨🇱') &
            (df['currency'] == 'CLP') & 
            (df['amount'].abs() > 500_000) & 
            (df['type'] != 'Income') &
            ~((df['type'] == 'Expense') & (df['category'] == 'Rental Apartment'))
        )
        high_clp = df[mask_clp]
        
        if not high_clp.empty:
            st.warning(f"{ICONS['warning']} Detectadas {len(high_clp)} transacciones en 'Main CLP 🇨🇱' > $500,000 (Excluyendo Income/Arriendo)")
            editable_transactions_dataframe(high_clp.sort_values("amount", ascending=False), key="val_high_clp")
        else:
            st.success(f"{ICONS['check']} Ninguna transacción en 'Main CLP 🇨🇱' supera los $500,000 (fuera de Arriendo/Income)")

        # 2b. Wallet: UNFCU (> 500 USD)
        mask_unfcu = (
            (df['wallet'] == 'UNFCU') &
            (df['currency'] == 'USD') &
            (df['amount'].abs() > 500) &
            (df['type'] != 'Income')
        )
        high_unfcu = df[mask_unfcu]

        if not high_unfcu.empty:
            st.warning(f"{ICONS['warning']} Detectadas {len(high_unfcu)} transacciones en 'UNFCU' > $500 USD")
            editable_transactions_dataframe(high_unfcu.sort_values("amount", ascending=False), key="val_high_unfcu")
        else:
            st.success(f"{ICONS['check']} Ninguna transacción en 'UNFCU' supera los $500 USD")
    
    # 3. Category & Type
    st.markdown("### 3. `category` & `type` ")
    
    # Check for missing categories
    nulos_cat = df[df['category'].isna() | (df['category'] == "")]
    if not nulos_cat.empty:
        st.error(f"{ICONS['close']} Detectadas {len(nulos_cat)} transacciones sin categoría")
        editable_transactions_dataframe(nulos_cat, key="val_nulos_cat")
    else:
        st.success(f"{ICONS['check']} Todas las transacciones tienen categoría")

    # Check for invalid types
    invalid_types = df[~df['type'].isin(['Expense', 'Income', 'Transfer'])]
    if not invalid_types.empty:
        st.error(f"{ICONS['close']} Detectados {len(invalid_types)} registros con tipo inválido (No es Expense o Income)")
        editable_transactions_dataframe(invalid_types, key="val_invalid_types")
    else:
        st.success(f"{ICONS['check']} Todos los tipos de transacción son válidos")

    # 4. Currency
    st.markdown("### 4. `currency` ")
    nulos_curr = df[df['currency'].isna() | (df['currency'] == "")]
    if not nulos_curr.empty:
        st.error(f"{ICONS['close']} Detectadas {len(nulos_curr)} transacciones sin moneda definida")
    else:
        st.success(f"{ICONS['check']} Todas las transacciones tienen moneda")
    
    # 5. Potential Duplicates
    st.markdown("### 5. Duplicados Potenciales")
    # Check for exact duplicates in date, amount, category and note
    cols_for_dupes = ['date', 'amount', 'category', 'note']
    dupes = df[df.duplicated(subset=cols_for_dupes, keep=False)]
    if not dupes.empty:
        st.warning(f"{ICONS['warning']} Detectados {len(dupes)} registros que podrían ser duplicados (Misma fecha, monto, categoría y nota)")
        editable_transactions_dataframe(dupes.sort_values("date"), key="val_dupes")
    else:
        st.success(f"{ICONS['check']} No se detectaron duplicados exactos")
    
