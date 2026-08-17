import pytest
import pandas as pd
import xml.etree.ElementTree as ET
from src.config import DB_URL
from unittest.mock import patch, MagicMock
from src.individual_apt_sales_etl import (
    read_district_code_five,
    return_df,
    convert_date_column,
    fetch_response
)
from requests.exceptions import ReadTimeout

# Helper function to create MagicMock object
def create_mock_response(xml_text):
    response = MagicMock()
    response.text = xml_text
    response.raise_for_status.return_value = None
    return response

def test_convert_date_colum():
    df = pd.DataFrame({
    "dealYear": ["2023", "2024"],
    "dealMonth": ["1", "12"]
    })

    result = convert_date_column(df)

    assert result.iloc[0]["deal_date"] == "202301"
    assert result.iloc[1]["deal_date"] == "202412"

def test_read_district_code_five():
    df = pd.DataFrame({
    "District": ["강남구", "종로구"],
    "Code": ["1168000000", "1200000000"]
    })

    result = read_district_code_five(df)

    assert result["강남구"] == "11680"
    assert result["종로구"] == "12000"

def test_return_df():
    api_response = '''
        <response>
            <body>
                <items>
                    <item>
                        <aptNm>래미안</aptNm>
                        <dealYear>2023</dealYear>
                        <dealMonth>1</dealMonth>
                    </item>
                </items>
            </body>
        </response>
    '''

    root = ET.fromstring(api_response)

    result = return_df(root)

    assert result.iloc[0]["aptNm"] == '래미안'
    assert result.iloc[0]["dealYear"] == '2023'
    assert result.iloc[0]["dealMonth"] == '1'

fake_response_xml = """
<response>
    <body>
        <totalCount>2</totalCount>
        <items>
            <item>
                <aptNm>래미안</aptNm>
                <dealYear>2023</dealYear>
                <dealMonth>1</dealMonth>
            </item>
            <item>
                <aptNm>자이</aptNm>
                <dealYear>2023</dealYear>
                <dealMonth>2</dealMonth>
            </item>
        </items>
    </body>
</response>
"""

def test_fetch_response_success():
    fake_response = create_mock_response(fake_response_xml)

    with patch("src.individual_apt_sales_etl.requests.get") as mock_get:
        mock_get.return_value = fake_response

        param = {
            "LAWD_CD": "11680",
            "DEAL_YMD": "202301",
            "numOfRows": 300
        }

        root, total_rows = fetch_response(
            param,
            "202301",
            "강남구"
        )

        assert mock_get.call_count == 1
        assert total_rows == 2
        assert root.findtext(".//aptNm") == "래미안"


@patch("src.individual_apt_sales_etl.requests.get")
def test_fetch_response_timeout_then_success(mock_get):
    fake_response = create_mock_response(fake_response_xml)

    mock_get.side_effect = [
        ReadTimeout,
        fake_response
    ]

    param = {
        "LAWD_CD": "11680",
        "DEAL_YMD": "202301",
        "numOfRows": 300
    }

    root, total_rows = fetch_response(
        param,
        "202301",
        "강남구"
    )

    assert mock_get.call_count == 2
    assert total_rows == 2
    assert root.findtext(".//aptNm") == "래미안"


@patch("src.individual_apt_sales_etl.requests.get")
def test_fetch_response_max_retries(mock_get):
    mock_get.side_effect = ReadTimeout

    param = {
        "LAWD_CD": "11680",
        "DEAL_YMD": "202301",
        "numOfRows": 300
    }

    with pytest.raises(RuntimeError):
        fetch_response(
            param,
            "202301",
            "강남구"
        )

    assert mock_get.call_count == 3