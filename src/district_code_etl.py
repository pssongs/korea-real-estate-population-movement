import pandas as pd
from sqlalchemy import text, create_engine
from src.config import DB_URL
from src.seoul_population_flow_etl import read_sql_file
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

def get_district_codes_records():
    df = pd.read_csv('/workspaces/korea-real-estate-population-movement/data/seoul_district_codes.csv')

    df['Code'] = df['Code'].astype(str)

    df = df.rename(columns={
        "District":"district",
        "Code":"code"})

    return df.to_dict(orient='records')

def main():
    engine = create_engine(DB_URL)
    records = get_district_codes_records()

    create_district_codes_table_query = read_sql_file('/workspaces/korea-real-estate-population-movement/sql/etl/create_district_code_dim_table.sql')
    insert_district_codes_query = read_sql_file('/workspaces/korea-real-estate-population-movement/sql/etl/insert_district_code.sql')

    with engine.begin() as conn:
        logger.info("Creating district codes table and inserting records")
        conn.execute(text(create_district_codes_table_query))
        logger.info("District codes table created")
        
        logger.info("Inserting district codes records")
        conn.execute(text(insert_district_codes_query),records)
        logger.info("District codes records inserted")

if __name__ == "__main__":
    main()