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

def get_apartment_sales_records():
    df = pd.read_csv('/workspaces/korea-real-estate-population-movement/data/seoul_apartments_sold.csv')

    # Drops rows that are headers and columns not needed, then renames a column
    df = df[2:].reset_index(drop=True).drop(columns=[
        "자치구별(1)"
        ]).rename(columns={
        "자치구별(2)":"district"
        })

    # Melts the DF to have a single column for month and units sold
    df = df.melt(
        id_vars=["district"],
        var_name="month",
        value_name="units_sold")

    # Converts the month column to YYYYMM format and converts it to an integer
    df["month"] = pd.to_datetime(
        df["month"].str.strip(),
        format="%Y. %m"
    ).dt.strftime("%Y%m").astype(int)

    return df.to_dict(orient="records")

def main():
    engine = create_engine(DB_URL)
    records = get_apartment_sales_records()

    create_apartment_sales_table_query = read_sql_file('/workspaces/korea-real-estate-population-movement/sql/create_apartment_sales_table.sql')
    insert_apartment_sales_query = read_sql_file('/workspaces/korea-real-estate-population-movement/sql/insert_apartment_sales.sql')

    with engine.begin() as conn:
        logger.info("Creating apartment sales table and inserting records")
        conn.execute(text(create_apartment_sales_table_query))
        logger.info("Apartment sales table created")


        logger.info("Inserting apartment sales records")
        conn.execute(text(insert_apartment_sales_query),records)
        logger.info("Apartment sales records inserted")

if __name__ == "__main__":
    main()