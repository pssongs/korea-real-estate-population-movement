from dotenv import load_dotenv
import os

load_dotenv(override=True)

START_DATE = 202301
END_DATE = 202512
BATCH_MONTHS = 3

POP_FLOW_SERVICE_KEY=os.getenv('POP_FLOW_SERVICE_KEY')
POP_FLOW_BASE_URL="https://apis.data.go.kr/1741000/ppltnDataStus/selectPpltnDataStus"

