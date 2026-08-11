from dotenv import load_dotenv
import os

load_dotenv(override=True)

POP_FLOW_SERVICE_KEY=os.getenv('POP_FLOW_SERVICE_KEY')
POP_FLOW_BASE_URL="https://apis.data.go.kr/1741000/ppltnDataStus/selectPpltnDataStus"

