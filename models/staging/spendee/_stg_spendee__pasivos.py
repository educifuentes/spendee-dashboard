from helpers.csv_loader import load_from_csv

def stg_spendee__pasivos():
    """
    Staging model for the pasivos Spendee account.
    Loads data via CSV from the path specified in _src_spendee.yml.
    """
    return load_from_csv("pasivos")
