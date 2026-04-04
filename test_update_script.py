import urllib.request
import pandas as pd
import numpy as np
from helpers.data_connection_cloud_sql import load_transactions, update_transaction

import logging
logging.basicConfig(level=logging.DEBUG)

df = load_transactions()
print(f"Loaded {len(df)} rows")
if not df.empty:
    row = df.iloc[0]
    
    # Simulate pandas fetching
    raw_id = row['id']
    row_id = int(raw_id) if pd.notnull(raw_id) else None
    
    print(f"Original ID type: {type(raw_id)} vs new ID type: {type(row_id)}")
    
    amount = float(row['amount'])
    print(f"Original amount type: {type(row['amount'])} vs new amount type: {type(amount)}")
    
    try:
        # User specified the exact error: [parameters: (-8990.0, np.float64(2560.0))]
        # where amount is -8990.0 and id is np.float64(2560.0)
        # So the ID is the np.float64 that is failing as "invalid input syntax for type bigint".
        print("Testing with int(row_id)...")
        update_transaction(int(row_id), {"amount": amount + 1.0})
        print(f"Update executed to amount {amount + 1.0}.")
        update_transaction(int(row_id), {"amount": amount})
        print(f"Restored to amount {amount}.")
    except Exception as e:
        import traceback
        traceback.print_exc()
else:
    print("No transactions found.")
