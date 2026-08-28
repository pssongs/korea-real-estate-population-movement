# Korea Real Estate Population Movement

---------

This project extracts Korean real estate transaction and population movement data from data.go.kr, transforms it with Pandas, and loads it into PostgreSQL for analysis. 

## Overview

### Collected Data
- Population movement between Seoul districts
- Individual apartment sale records in Seoul
- Seoul apartment transaction data
- District Information

With this data, we will explore the correlation between population movement, apartment sales, and apartment prices across Seoul, and identify districts with significant trends. 

Future analysis will expand the project to include jeonse (전세) and wolsae (월세) housing data to investigate broader housing market trends.

### Pipeline

```text
Government APIs / CSV
        ↓
     Python
        ↓
    Pandas
        ↓
 Transformation
        ↓
   PostgreSQL
        ↓
     Analysis
```

### Project Structure
```text
korea-real-estate-population-movement/
│
├── data/
├── notebook/
├── sql/
├── src/
├── tests/
├── requirements.txt
└── README.md
└── final_analysis.ipynb

src/        ETL pipeline code
tests/      pytest tests
sql/        SQL schema and insert statements
data/       supporting data such as district codes
notebook/   experimentation
```

### Technologies Used
- Python
- Pandas
- Requests
- SQLAlchemy
- PostgreSQL
- Pytest
- NumPy
- Matplotlib

## Setup / Installation
```bash
git clone <repository>
cd korea-real-estate-population-movement

python -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
```

Variables in my .env file:
- SERVICE_KEY
    - Obtained through data.go.kr
- DB_URL

## Running the Pipeline
With your workspace in the korea-real-estate-population-movement:
```bash
python 'src/seoul_population_flow_etl.py'
python 'src/individual_apt_sales_etl.py'
```
Seoul population flow ETL will extract data on inflow and outflow of residents on all 25 districts in Seoul. Then, it will transform the extracted XML into a pandas Dataframe and cleaned before converting in to records. Finally, the transformed response will be uploaded into the database for analysis

Individual apartment sales ETL likewise extracts data from data.go.kr. The extracted data contains records of apartment transaction records in the observation period. The data is cleaned by removing unwanted fields and renaming columns before being loaded into PostgreSQL.

## Reverse ETL

Transformed monthly real-estate metrics are synchronized from PostgreSQL to Google Sheets.

**Data Flow:**
```text
Korean Public Data
       ↓
     ETL
       ↓
   PostgreSQL
       ↓
  SQL Transformation
       ↓
Monthly district-level price metrics
       ↓
 Reverse ETL
       ↓
 Google Sheets
 ```

* **Grain:** One row per district + month
* **Business key:** `(district, month)`
* **Incremental loading:** New records are inserted while existing records are updated only when the value changes.
* **Idempotent** 
* **Batching:** New rows and changed rows are sent in batches to reduce Google Sheets API calls.
* **Data types:** PostgreSQL `Decimal` values are converted to `float` when preparing the Google Sheets API payload.

## Data Modeling & Analysis

* **Grain:** Transaction-level source data → district/month analytical data
* **Business keys:** Used to identify records across systems and support incremental loading.
* **OLTP vs OLAP:** Transaction data is detailed and event oriented; aggregated monthly metrics support analytical workloads.
* **Dimensional modeling:** The project uses a dimensional modeling approach by separating transaction data from district reference information.
* **Weighted average:** Monthly price/m² is calculated using total transaction value ÷ total transaction area.


## Testing
```bash
python -m pytest 'tests/individual_apt_sales_test.py'
python -m pytest 'tests/seoul_population_flow_test.py'
```

Test covers API success, timeout/retry behavior, response parsing, and data transformation. 

## Future Improvements
- Automate monthly extraction with GitHub Actions
- Improve API retry and backoff handling
- Add data quality checks
