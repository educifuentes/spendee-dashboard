import pandas as pd
import sys
import os

# Add project root to sys.path
sys.path.append(os.getcwd())

from models.staging._stg_spendee__transactions import stg_spendee__transactions

try:
    print("Testing stg_spendee__transactions()...")
    df = stg_spendee__transactions()
    print(f"DataFrame shape: {df.shape}")
    print("DataFrame Head:")
    print(df.head())
    
    if not df.empty:
        print("\nSUCCESS: Data loaded successfully.")
    else:
        print("\nWARNING: DataFrame is empty.")
except Exception as e:
    print(f"\nERROR: {e}")
    import traceback
    traceback.print_exc()
