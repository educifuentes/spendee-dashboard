import os
import re

from helpers.constants.wallets import WALLETS

data_dir = "seeds/new_transaction uploads"
if not os.path.exists(data_dir):
    print(f"Directory {data_dir} does not exist")
else:
    files = os.listdir(data_dir)
    print(f"Files in {data_dir}: {files}")
    
    # We want to find the latest date for each wallet
    # Format: transactions_export_YYYY-MM-DD_walletname.csv
    
    latest_files = {}
    pattern = re.compile(r"transactions_export_(\d{4}-\d{2}-\d{2})_(.+)\.csv")
    
    for f in files:
        match = pattern.match(f)
        if match:
            date_str = match.group(1)
            wallet_name = match.group(2)
            
            if wallet_name in WALLETS:
                if wallet_name not in latest_files or date_str > latest_files[wallet_name]['date']:
                    latest_files[wallet_name] = {'date': date_str, 'file': f}
                    
    print("Latest files to load:", latest_files)
