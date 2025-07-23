import pandas as pd
import sqlite3

# Load CSVs
eligibility = pd.read_csv("data/eligiblilty.csv")
ad_sales = pd.read_csv("data/Ad sales.csv")
total_sales = pd.read_csv("data/Total sales.csv")

# Connect to SQLite DB
conn = sqlite3.connect("database/ecommerce.db")

# Write tables
eligibility.to_sql("eligibility", conn, if_exists="replace", index=False)
ad_sales.to_sql("ad_sales", conn, if_exists="replace", index=False)
total_sales.to_sql("total_sales", conn, if_exists="replace", index=False)

print("CSV files loaded into SQLite DB successfully.")
