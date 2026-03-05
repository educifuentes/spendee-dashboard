import urllib.request
import pandas as pd
from utilities.data_connection_cloud_sql import load_transactions, update_transaction

import logging
logging.basicConfig(level=logging.DEBUG)

df = load_transactions()
print(f"Loaded {len(df)} rows")
if not df.empty:
    row = df.iloc[0]
    print(f"Original: {row['id']}, amount: {row['amount']}, type: {row['type']}")
    try:
        update_transaction(row['id'], {"amount": row['amount'] + 1})
        print(f"Update executed to amount {row['amount'] + 1}.")
        update_transaction(row['id'], {"amount": row['amount']})
        print(f"Restored to amount {row['amount']}.")
    except Exception as e:
        import traceback
        traceback.print_exc()
else:
    print("No transactions found.")
