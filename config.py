from dotenv import load_dotenv
import os

load_dotenv(override=True)

DB_URL = os.getenv('DB_URL')

START_DATE = 202301
END_DATE = 202607
BATCH_MONTHS = 3

POP_FLOW_SERVICE_KEY=os.getenv('POP_FLOW_SERVICE_KEY')
POP_FLOW_BASE_URL="https://apis.data.go.kr/1741000/ppltnDataStus/selectPpltnDataStus"
POP_FLOW_COLUMNS = ["statsYm",   
        "mvinCtpvNm",
        "mvinSggNm",
        "mvtCtpvNm",
        "mvtSggNm",
        "totNmprCnt",
        "maleNmprCnt",
        "femlNmprCnt",        
    ]
