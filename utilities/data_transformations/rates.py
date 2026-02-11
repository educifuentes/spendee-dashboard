import pandas as pd
from pathlib import Path

def get_usd_clp_rates_map():
    """
    Load USD to CLP rates from the constants CSV file and return as a mapping dict {month: rate}.
    """
    # Assuming the project structure and that this file is in utilities/data_transformations/
    # The rates file is expected in utilities/constants/usd_clp_rates.csv
    project_root = Path(__file__).parent.parent
    rates_path = project_root / "constants" / "usd_clp_rates.csv"
    
    if not rates_path.exists():
        # Fallback to a wider search if not found (e.g. from repo root)
        rates_path = Path("utilities/constants/usd_clp_rates.csv")
        
    if not rates_path.exists():
        return {}

    rates_df = pd.read_csv(rates_path)
    return dict(zip(rates_df["month"], rates_df["rate"]))
