import pandas as pd

from utilities.yaml_loader import get_table_config


def stg_spendee__transactions() -> pd.DataFrame:
    """data of all wallets into one transaction sdataframe"""

    source_yaml = 'models/staging/_src_spendee.yml'
    table_names = ['main-clp', 'unfcu', 'pasivos']
    
    dfs = []
    for table_name in table_names:
        table_config = get_table_config('spendee', table_name, yaml_path=source_yaml)
        if table_config and 'path' in table_config:
            df_temp = pd.read_csv(table_config['path'])
            dfs.append(df_temp)
    
    if not dfs:
        return pd.DataFrame()

    df = pd.concat(dfs, ignore_index=True)

    # dtypes
    df["Date"] = pd.to_datetime(df["Date"])
    
    return df


