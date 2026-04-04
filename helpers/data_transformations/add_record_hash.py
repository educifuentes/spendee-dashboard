import pandas as pd
import hashlib

def add_record_hash(df, columns=None):
    """
    Generates a record hash based on specified columns and adds it to the dataframe.
    """
    if columns is None:
        # Default columns to hash if none provided
        columns = df.columns.tolist()

    def generate_hash(row):
        # Concatenate values of specified columns, using string representation
        # Handle nulls by using 'None' string
        content = "|".join([str(row[col]) for col in columns])
        return hashlib.md5(content.encode()).hexdigest()

    df["record_hash"] = df.apply(generate_hash, axis=1)
    return df