import pandas as pd
from sqlalchemy import text, create_engine
from config import DB_URL
import gspread
from google.oauth2.service_account import Credentials

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

credentials = Credentials.from_service_account_file(
    "credentials.json",
    scopes=SCOPES
)

client = gspread.authorize(credentials)

spreadsheet = client.open_by_key('17jfM_ifrt0BltTI1l-pptB1igFcvOFGc7xirtuTNB-g')
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

# Creates a key column for the extracted data
df['key'] = list(zip(df["district"], df["month"]))

# Creates a key column for the existing data
existing_df["key"] = list(
    zip(existing_df["district"], existing_df["month"])
)

new_rows = df[~df["key"].isin(existing_df["key"])]
key_existing_rows = df[df["key"].isin(existing_df["key"])]

# Dictionary to  know which row corresponds to each key
key_to_row = {
    (row["district"], row["month"]): i + 2
    for i, row in enumerate(existing_data)
}

# Batch Updates
updates = []

for _, row in key_existing_rows.iterrows():
    key = row['key']

    new_value = float(row['weighted_avg_price_m2'])
    existing_value = float(
        existing_df.loc[
            existing_df['key'] == key,
            'weighted_avg_price_m2'
            ].iloc[0]
            )
    
    if new_value != existing_value:
        sheet_row = key_to_row[key]

        updates.append({
            "range": f"C{sheet_row}",
            "values": [[float(new_value)]]
        })

if updates:
    worksheet.batch_update(updates)

# Batch Inserts
new_values = new_rows[
    ['district', 'month', 'weighted_avg_price_m2']
].copy()

new_values['weighted_avg_price_m2'] = (
    new_values['weighted_avg_price_m2'].astype(float)
)

new_values = new_values.values.tolist()

if new_values:
    start_row = len(existing_data) + 2

    worksheet.update(
        f"A{start_row}:C{start_row + len(new_values) - 1}",
        new_values
    )