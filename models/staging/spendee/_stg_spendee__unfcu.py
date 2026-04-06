from helpers.csv_loader import load_from_csv

def stg_spendee__unfcu():
    """
    Staging model for the unfcu Spendee account.
    Loads data via CSV from the path specified in _src_spendee.yml.
    """
    return load_from_csv("unfcu")
