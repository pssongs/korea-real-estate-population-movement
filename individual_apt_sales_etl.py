import pandas as pd
import requests, time, logging
import xml.etree.ElementTree as ET
from sqlalchemy import text, create_engine
from config import SERVICE_KEY, APT_SALES_BASE_URL, APT_SALES_COLUMNS, END_DATE, DB_URL
from seoul_population_flow_etl  import read_sql_file

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

# Returns a dict mapping district name to the first 5 numbers of respective code
def read_district_code_five_csv():
    df = pd.read_csv('/workspaces/korea-real-estate-population-movement/data/seoul_district_codes.csv')

    required = {"District","Code"}

    if not required.issubset(df.columns):
        logger.error('seoul_district_codes.csv is missing required columns.')
        raise ValueError("CSV missing required columns.")

    df["District"] = df["District"].str.strip()
    df["Code"] = df["Code"].astype(str).str[:5]

    return dict(zip(df['District'],df['Code']))

# Takes in XML text and returns a DataFrame with the relevant columns
def return_df(root):
    items = root.findall(".//item")
    data = []

    for item in items:
        row = {}

        for child in item:
            if child.tag in APT_SALES_COLUMNS:
                row[child.tag] = child.text.strip() if child.text else None

        data.append(row)

    return pd.DataFrame(data)

def rename_df(df):
    return df.rename(columns={
        "aptNm":"apt_name",
        "sggCd":"district_code",
        "buildYear":"build_year"
    })

# Creates 6 digit date column yyyymm
def convert_date_column(df):
    df["deal_date"] = (
        df["dealYear"].astype(str)
        + df["dealMonth"].astype(str).str.zfill(2)
    )

    return df.drop(columns=["dealYear","dealMonth"])

def main():
    max_retries = 3
    district_info = read_district_code_five_csv()

    engine = create_engine(DB_URL,
                           pool_pre_ping=True)

    create_individual_apt_sales_table_sql = read_sql_file('/workspaces/korea-real-estate-population-movement/sql/create_individual_apt_sales_table.sql')
    with engine.begin() as conn:
        conn.execute(text(create_individual_apt_sales_table_sql))

    current_date = pd.to_datetime('202303',format='%Y%m')
    end_date = pd.to_datetime(END_DATE,format='%Y%m')
    while current_date <= end_date:
        data = []
        date = current_date.strftime(format='%Y%m')

        for district in district_info:

            param = {
            'LAWD_CD':district_info[district],
            'DEAL_YMD':date,
            'serviceKey': SERVICE_KEY,
            'numOfRows':300,
            'pageNo':1 
            }

            for attempt in range(max_retries):
                try:
                    response = requests.get(
                        APT_SALES_BASE_URL,
                        params=param,
                        timeout=30)
                    response.raise_for_status()

                    root = ET.fromstring(response.text)

                    total_rows = int(root.findtext('.//totalCount', default='0'))

                    # If the total count of rows for district exceeds 300, attempting with the totalCount
                    if total_rows > 300:
                        logger.info(f'attempt {attempt+1}: Total_rows exceeds 200: attempting again...'
                              f'numOfRows has been set to {total_rows}')

                        param = {
                        'LAWD_CD':district_info[district],
                        'DEAL_YMD':date,
                        'serviceKey': SERVICE_KEY,
                        'numOfRows':total_rows,
                        'pageNo':1 
                        }

                        response = requests.get(
                            APT_SALES_BASE_URL,
                            params=param,
                            timeout=30)
                        response.raise_for_status()

                        root = ET.fromstring(response.text)

                    df = rename_df(
                        convert_date_column(
                            return_df(root)
                        )
                    )

                    logger.info(f"fetched {district} info")

                    data.append(df)
                    break

                except requests.exceptions.ReadTimeout:
                    logger.warning(
                        f"Timeout: {current_date} info of {district} "
                        f"(attempt {attempt + 1}/{max_retries})"
                    )

                    if attempt < max_retries - 1:
                        time.sleep(2)
            else:
                logger.error(
                    f"Failed to fetch {current_date} info of {district} "
                    f"after {max_retries} attempts."
                )
                raise RuntimeError()

        result = pd.concat(data, ignore_index=True).to_dict(orient="records")
        insert_individual_apt_sales_sql = read_sql_file('/workspaces/korea-real-estate-population-movement/sql/insert_individual_apt_sales.sql')

        with engine.begin() as conn:
            logger.info(f"Inserting {current_date} data into DB...")
            conn.execute(text(insert_individual_apt_sales_sql), result)
            logger.info(f"Successfully inserted {current_date} data into DB.")


        current_date += pd.DateOffset(months=1)

if __name__ == "__main__": 
    main()