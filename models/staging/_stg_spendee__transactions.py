import pandas as pd

from utilities.data_connection_cloud_sql import load_transactions


def stg_spendee__transactions():
    df = load_transactions()

    return df