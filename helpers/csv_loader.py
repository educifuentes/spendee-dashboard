import pandas as pd
import os
from helpers.yaml_loader import get_table_config

def load_from_csv(table_name, source_name='spendee', yaml_path='models/sources/spendee/_src_spendee.yml'):
    """
    Loads a specific Spendee table from CSV using the path defined in the YAML source config.
    """
    config = get_table_config(source_name, table_name, yaml_path=yaml_path)
    if not config:
        raise ValueError(f"No config found for table '{table_name}' in source '{source_name}' at '{yaml_path}'")
    
    path = config.get('path')
    
    # Resolve path relative to project root
    # Since this file is in helpers/, project root is one level up
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    full_path = os.path.join(project_root, path)
    
    if not os.path.exists(full_path):
         raise FileNotFoundError(f"CSV file not found for table '{table_name}' at: {full_path}")
    
    df = pd.read_csv(full_path)
    
    # Internal rename map to ensure consistent internal schema
    RENAME_MAP = {
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
    
    df = df.rename(columns=RENAME_MAP)
    
    # Parse date if present
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
    
    # Keep only columns defined in the rename map
    keep_cols = [c for c in RENAME_MAP.values() if c in df.columns]
    return df[keep_cols]
