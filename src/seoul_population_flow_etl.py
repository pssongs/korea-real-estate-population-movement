import requests, time, logging
from .config import (
    POP_FLOW_BASE_URL,
    SERVICE_KEY,
    POP_FLOW_COLUMNS,
    START_DATE,
    END_DATE,
    BATCH_MONTHS,
    DB_URL)
import pandas as pd
import xml.etree.ElementTree as ET
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

# Creates engine to connect to DB
def create_db_engine():
    return create_engine(
        DB_URL,
        pool_pre_ping=True)

# Helper function to read sql file
def read_sql_file(path):
    with open(path,"r") as f:
        return f.read()

# Reads csv with name of district and its respective code and returns a dict
def read_districts_csv():
    df = pd.read_csv('/workspaces/korea-real-estate-population-movement/data/seoul_district_codes.csv')

    required = {"District","Code"}

    if not required.issubset(df.columns):
        logger.error('seoul_district_code.csv is missing required columns')
        raise ValueError("CSV missing required columns.")

    df["District"] = df["District"].str.strip()
    df["Code"] = pd.to_numeric(df["Code"], errors="raise")

    return dict(zip(df['District'],df['Code']))

# Takes a XML response's text and returns a DataFrame
def return_df(root):
    items = root.findall(".//item")
    data = []

    for item in items:
        row = {}

        for child in item:
            if child.tag in POP_FLOW_COLUMNS:
                row[child.tag] = child.text.strip() if child.text else None

        data.append(row)

    return pd.DataFrame(data)

def rename_columns(df):
    return df.rename(columns={
    "statsYm":"date",
    "mvinCtpvNm":"from_province",
    "mvtCtpvNm":"to_province",
    "mvinSggNm":"from_district",
    "mvtSggNm":"to_district",
    "totNmprCnt":"total_people",
    "maleNmprCnt":"male",
    "femlNmprCnt":"female"})

# Fetches API requests for all district combination from inputted start and end date
def get_population_flow(districts, start_date, end_date):
    dfs = []
    completed = 0
    total = len(districts) ** 2
    max_retries = 3

    for origin in districts:
        for destination in districts:

            param = {
                "serviceKey": SERVICE_KEY,
                "mvinAdmmCd": districts[origin],
                "mvtAdmmCd": districts[destination],
                "srchFrYm": start_date,
                "srchToYm": end_date,
                "lv": 2,
                "type": "XML",
                "numOfRows": BATCH_MONTHS
            }

            for attempt in range(max_retries):
                try:
                    response = requests.get(
                        POP_FLOW_BASE_URL,
                        params=param,
                        timeout=30
                    )

                    response.raise_for_status()

                    root = ET.fromstring(response.text)

                    df = rename_columns(return_df(root))
                    dfs.append(df)

                    completed += 1

                    logger.info(
                        f'{completed}/{total}: '
                        f'Fetched {origin} to {destination}'
                    )

                    break

                except requests.exceptions.ReadTimeout:
                    logger.warning(
                        f"Timeout: {origin} -> {destination} "
                        f"(attempt {attempt + 1}/{max_retries})"
                    )

                    if attempt < max_retries - 1:
                        time.sleep(2)
                except requests.exceptions.HTTPError as e:
                    if response.status_code == 503:
                        logger.warning(
                            f"API unavailable (503): {origin} -> {destination} "
                            f"(attempt {attempt + 1}/{max_retries})"
                        )

                        if attempt < max_retries - 1:
                            time.sleep(5)
            else:
                logger.error(
                    f"Failed after {max_retries} attempts: "
                    f"{origin} -> {destination}"
                )
                raise RuntimeError()
            
    logger.info(f"Extraction complete: {completed}/{total} API requests")
    return pd.concat(dfs, ignore_index=True)

# Splits the date range into 3 month batches
def generate_date_batches(start_date,end_date):
    current = pd.to_datetime(start_date, format='%Y%m')
    end = pd.to_datetime(end_date, format='%Y%m')

    date_batches = []

    while current <= end:
        batch_end = min(
            current + pd.DateOffset(months=2),
            end
        )

        current_batch = [
            current.strftime('%Y%m'),
            batch_end.strftime('%Y%m')
            ]

        date_batches.append(current_batch)   

        current = batch_end + pd.DateOffset(months=1)
    return date_batches

# Loads the population flow records to DB
def load_seoul_population_flow(conn, df):
    records = df.to_dict(orient='records')
    batch_size = 100

    insert_query = read_sql_file('/workspaces/korea-real-estate-population-movement/sql/insert_seoul_population_flow.sql')

    # Loads records in batches due to load management
    for i in range(0,len(records),batch_size):
      batch = records[i:i + batch_size]
      conn.execute(text(insert_query),batch)

      logger.info(f"{min(i + batch_size,len(records))}/{len(records)} inserted")

def main():
   date_batches = generate_date_batches(START_DATE,END_DATE)
   districts = read_districts_csv()
   engine = create_db_engine()

   create_table_query = read_sql_file('/workspaces/korea-real-estate-population-movement/sql/create_seoul_population_flow_table.sql')

   with engine.begin() as conn:
       conn.execute(text(create_table_query))

   for start,end in date_batches[-2:]:

      start_time = time.time()

      logger.info(f"Starting batch: {start} -> {end}")

      result = get_population_flow(
          districts,
          start,
          end)

      extraction_time = time.time() - start_time
      load_start_time = time.time()
      for attempt in range(3):
         try: 
            with engine.begin() as conn:
               load_seoul_population_flow(conn,result)

            break
         except OperationalError:
            logger.warning(f"DB connection failed. Retry {attempt+1}/3")

      else:
         logger.error(f"Failed to load batch {start} -> {end} after 3 attempts")
         raise RuntimeError()
      elapsed = time.time() - start_time  
      load_time = time.time() - load_start_time
      logger.info(
          f"Completed batch: {start} -> {end}"
          f"Extraction: {extraction_time:.2f} seconds"
          f"Database Load: {load_time:.2f} seconds"
          f"Total: {elapsed:.2f} seconds"
          )

if __name__ == "__main__":
    main()