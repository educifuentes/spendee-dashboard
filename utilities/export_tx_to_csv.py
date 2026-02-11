import os
import sys
import pandas as pd
from datetime import datetime

# Add the project root to the python path so we can import from models
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.append(project_root)

from models.marts._fct_transactions import fct_transactions

def export_transactions_to_csv(output_path=None):
    """
    Loads transactions from the fct_transactions model and exports them to a CSV file.
    """
    print("🚀 Loading transactions from fct_transactions...")
    try:
        df = fct_transactions()
        
        if df.empty:
            print("⚠️ No transactions found to export.")
            return

        # Default path setup
        if output_path is None:
            # Get project root
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            seeds_dir = os.path.join(base_dir, "seeds", "uploads")
            
            # Create directory if it doesn't exist
            if not os.path.exists(seeds_dir):
                print(f"📁 Creating directory {seeds_dir}...")
                os.makedirs(seeds_dir)
                
            output_path = os.path.join(seeds_dir, "fct_transactions.csv")

        print(f"📦 Exporting {len(df)} transactions to {output_path}...")
        df.to_csv(output_path, index=False)
        print("✅ Export complete!")
        
    except Exception as e:
        print(f"❌ Error during export: {str(e)}")

if __name__ == "__main__":
    export_transactions_to_csv()