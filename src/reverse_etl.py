import pandas as pd
from sqlalchemy import text, create_engine
from config import DB_URL
import gspread
from google.oauth2.service_account import Credentials
from gspread_dataframe import set_with_dataframe

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

credentials = Credentials.from_service_account_file(
    "credentials.json",
    scopes=SCOPES
)

client = gspread.authorize(credentials)

spreadsheet = client.open("Seoul Real Estate Monthly Price")
worksheet = spreadsheet.sheet1

existing_data = worksheet.get_all_records()
existing_df = pd.DataFrame(existing_data)

engine = create_engine(
    DB_URL
)

with open('/workspaces/korea-real-estate-population-movement/sql/etl/reverse_etl.sql','r') as f:
    query = f.read()


with engine.begin() as conn:
    result = conn.execute(text(query))

df = pd.DataFrame(result)

df['key'] = list(zip(df["district"], df["month"]))

existing_df["key"] = list(
    zip(existing_df["district"], existing_df["date"])
)

new_rows = df[~df["key"].isin(existing_df["key"])]
existing_rows = df[df["key"].isin(existing_df["key"])]

# Dictionary to  know which row corresponds to each key
key_to_row = {
    (row["district"], row["date"]): i + 2
    for i, row in enumerate(existing_data)
}

# Batch Updates
updates = []

for _, row in existing_rows.iterrows():

    key = row["key"]
    sheet_row = key_to_row[key]

    updates.append({
        "range": f"C{sheet_row}",
        "values": [[row["avg_price_m2"]]]
    })

if updates:
    worksheet.batch_update(updates)


# Batch Inserts
new_values = new_rows[
    ["district", "month", "avg_price_m2"]
].values.tolist()

if new_values:
    start_row = len(existing_data) + 2

    worksheet.update(
        f"A{start_row}:C{start_row + len(new_values) - 1}",
        new_values
    )