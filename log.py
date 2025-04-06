import pandas as pd
import sqlite3

conn = sqlite3.connect("power_data.db")
df = pd.read_sql_query("SELECT * FROM power_log", conn)
print(df.tail())
