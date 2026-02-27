import pandas as pd
from scripts.database_add_new_transactions import get_db_connection

engine = get_db_connection()
query = "SELECT MAX(date) as max_date FROM transactions"
df = pd.read_sql(query, engine)
max_date = df["max_date"].iloc[0]
print("Type of max_date:", type(max_date))
print("Value:", max_date)
if hasattr(max_date, 'tzinfo'):
    print("TZ info:", max_date.tzinfo)
