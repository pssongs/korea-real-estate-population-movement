import pytest
from src.config import DB_URL
from unittest.mock import patch, MagicMock
from src.seoul_population_flow_etl import return_df, generate_date_batches, get_population_flow
import xml.etree.ElementTree as ET
from requests.exceptions import ReadTimeout


def test_return_df():
    response = '''
        <body>
            <items>
                <item>
                    <statsYm>202301</statsYm>
                    <mvinAdmmCd>1114000000</mvinAdmmCd>
                    <mvtAdmmCd>1111000000</mvtAdmmCd>
                    <mvinCtpvNm>서울특별시</mvinCtpvNm>
                    <mvtCtpvNm>서울특별시</mvtCtpvNm>
                    <mvinSggNm>중구</mvinSggNm>
                    <mvtSggNm>종로구</mvtSggNm>
                    <totNmprCnt>35</totNmprCnt>
                    <maleNmprCnt>19</maleNmprCnt>
                    <femlNmprCnt>16</femlNmprCnt>
                </item>
                <item>
                    <statsYm>202301</statsYm>
                    <mvinAdmmCd>1117000000</mvinAdmmCd>
                    <mvtAdmmCd>1114000000</mvtAdmmCd>
                    <mvinCtpvNm>서울특별시</mvinCtpvNm>
                    <mvtCtpvNm>서울특별시</mvtCtpvNm>
                    <mvinSggNm>강남구</mvinSggNm>
                    <mvtSggNm>중구</mvtSggNm>
                    <totNmprCnt>110</totNmprCnt>
                    <maleNmprCnt>84</maleNmprCnt>
                    <femlNmprCnt>16</femlNmprCnt>
                </item>
            </items>
        </body>
    '''

    root = ET.fromstring(response)

    df = return_df(root)

    assert len(df) == 2
    assert df.iloc[0]["mvinCtpvNm"] == "서울특별시"
    assert df.iloc[1]["totNmprCnt"] == "110"

def test_generate_date_batches():
    start_date = "201305"
    end_date = "201412"

    df = generate_date_batches(start_date,end_date)

    assert len(df) == 7
    assert df[0] == ["201305","201307"]
    assert df[6] == ["201411","201412"]
    assert df[1][1] == "201310"

@patch('src.seoul_population_flow_etl.requests.get')
def test_get_population_flow_timeout(mock_get):
    mock_get.side_effect = ReadTimeout

    mock_districts = {
        "강남구":"1114000000",
        "종로구":"1111000000"
    }

    start = "202301"
    end = "202303"

    with pytest.raises(RuntimeError):
        get_population_flow(mock_districts,start,end)

    assert mock_get.call_count == 3
