from helpers.csv_loader import load_from_csv

def stg_spendee__main_clp():
    """
    Staging model for the main-clp Spendee account.
    Loads data via CSV from the path specified in _src_spendee.yml.
    """
    return load_from_csv("main-clp")
