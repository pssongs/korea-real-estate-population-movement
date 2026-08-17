import pytest
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

# Check if it retries 3 times and raises RunTimeError
@patch('src.seoul_population_flow_etl.requests.get')
def test_get_population_flow_timeout(mock_get):
    mock_get.side_effect = ReadTimeout

    mock_districts = {
        "강남구":"1114000000",
        "종구":"1111000000"
    }

    start = "202301"
    end = "202303"

    with pytest.raises(RuntimeError):
        get_population_flow(mock_districts,start,end)

    assert mock_get.call_count == 3

# Helper function to create MagicMock object for below two tests
def create_mock_response(xml_text):
    response = MagicMock()
    response.text = xml_text
    response.raise_for_status.return_value = None
    return response

@patch('src.seoul_population_flow_etl.requests.get')
def test_get_population_flow_retry(mock_get):
    gangnam_gangnam_xml = '''
        <body>
            <items>
                <item>
                    <statsYm>202301</statsYm>
                    <mvinAdmmCd>1114000000</mvinAdmmCd>
                    <mvtAdmmCd>1114000000</mvtAdmmCd>
                    <mvinCtpvNm>서울특별시</mvinCtpvNm>
                    <mvtCtpvNm>서울특별시</mvtCtpvNm>
                    <mvinSggNm>강남구</mvinSggNm>
                    <mvtSggNm>강남구</mvtSggNm>
                    <totNmprCnt>110</totNmprCnt>
                    <maleNmprCnt>84</maleNmprCnt>
                    <femlNmprCnt>26</femlNmprCnt>
                </item>
            </items>
        </body>
    '''
    gangnam_gangnam_response = create_mock_response(gangnam_gangnam_xml)

    gangnam_gwangjingu_xml = '''
        <body>
            <items>
                <item>
                    <statsYm>202301</statsYm>
                    <mvinAdmmCd>1114000000</mvinAdmmCd>
                    <mvtAdmmCd>1128000000</mvtAdmmCd>
                    <mvinCtpvNm>서울특별시</mvinCtpvNm>
                    <mvtCtpvNm>서울특별시</mvtCtpvNm>
                    <mvinSggNm>강남구</mvinSggNm>
                    <mvtSggNm>광진구</mvtSggNm>
                    <totNmprCnt>75</totNmprCnt>
                    <maleNmprCnt>40</maleNmprCnt>
                    <femlNmprCnt>35</femlNmprCnt>
                </item>
            </items>
        </body>
    '''
    gangnam_gwangjingu_response = create_mock_response(gangnam_gwangjingu_xml)

    gwangjingu_gangnam_xml = '''
            <body>
            <items>
                <item>
                    <statsYm>202301</statsYm>
                    <mvinAdmmCd>1128000000</mvinAdmmCd>
                    <mvtAdmmCd>1114000000</mvtAdmmCd>
                    <mvinCtpvNm>서울특별시</mvinCtpvNm>
                    <mvtCtpvNm>서울특별시</mvtCtpvNm>
                    <mvinSggNm>광진구</mvinSggNm>
                    <mvtSggNm>강남구</mvtSggNm>
                    <totNmprCnt>60</totNmprCnt>
                    <maleNmprCnt>32</maleNmprCnt>
                    <femlNmprCnt>28</femlNmprCnt>
                </item>
            </items>
        </body>
    '''
    gwangjingu_gangnam_response = create_mock_response(gwangjingu_gangnam_xml)

    gwangjingu_gwangjingu_xml = '''
        <body>
            <items>
                <item>
                    <statsYm>202301</statsYm>
                    <mvinAdmmCd>1128000000</mvinAdmmCd>
                    <mvtAdmmCd>1128000000</mvtAdmmCd>
                    <mvinCtpvNm>서울특별시</mvinCtpvNm>
                    <mvtCtpvNm>서울특별시</mvtCtpvNm>
                    <mvinSggNm>광진구</mvinSggNm>
                    <mvtSggNm>광진구</mvtSggNm>
                    <totNmprCnt>90</totNmprCnt>
                    <maleNmprCnt>48</maleNmprCnt>
                    <femlNmprCnt>42</femlNmprCnt>
                </item>
            </items>
        </body>

    '''
    gwangjingu_gwangjingu_response = create_mock_response(gwangjingu_gwangjingu_xml)

    mock_districts = {
        "강남구":"1114000000",
        "광진구":"1128000000"
    }


    mock_get.side_effect = [
        ReadTimeout,
        gangnam_gangnam_response,
        gangnam_gwangjingu_response,
        gwangjingu_gangnam_response,
        gwangjingu_gwangjingu_response
    ]

    start = "202301"
    end = "202303"

    result = get_population_flow(
        mock_districts,
        start,
        end
    )

    assert mock_get.call_count == 5
    assert len(result) == 4

    assert result.iloc[0]["date"] == "202301"
    assert result.iloc[0]["from_district"] == "강남구"
    assert result.iloc[0]["to_district"] == "강남구"
    assert result.iloc[0]["total_people"] == "110"

    params = mock_get.call_args.kwargs["params"]


    assert params["lv"] == 2
    assert params["type"] == "XML"

@patch('src.seoul_population_flow_etl.requests.get')
def test_get_population_flow_success(mock_get):
    gangnam_gangnam_xml = '''
        <body>
            <items>
                <item>
                    <statsYm>202301</statsYm>
                    <mvinAdmmCd>1114000000</mvinAdmmCd>
                    <mvtAdmmCd>1114000000</mvtAdmmCd>
                    <mvinCtpvNm>서울특별시</mvinCtpvNm>
                    <mvtCtpvNm>서울특별시</mvtCtpvNm>
                    <mvinSggNm>강남구</mvinSggNm>
                    <mvtSggNm>강남구</mvtSggNm>
                    <totNmprCnt>110</totNmprCnt>
                    <maleNmprCnt>84</maleNmprCnt>
                    <femlNmprCnt>26</femlNmprCnt>
                </item>
            </items>
        </body>
    '''
    gangnam_gangnam_response = create_mock_response(gangnam_gangnam_xml)

    gangnam_gwangjingu_xml = '''
        <body>
            <items>
                <item>
                    <statsYm>202301</statsYm>
                    <mvinAdmmCd>1114000000</mvinAdmmCd>
                    <mvtAdmmCd>1128000000</mvtAdmmCd>
                    <mvinCtpvNm>서울특별시</mvinCtpvNm>
                    <mvtCtpvNm>서울특별시</mvtCtpvNm>
                    <mvinSggNm>강남구</mvinSggNm>
                    <mvtSggNm>광진구</mvtSggNm>
                    <totNmprCnt>75</totNmprCnt>
                    <maleNmprCnt>40</maleNmprCnt>
                    <femlNmprCnt>35</femlNmprCnt>
                </item>
            </items>
        </body>
    '''
    gangnam_gwangjingu_response = create_mock_response(gangnam_gwangjingu_xml)

    gwangjingu_gangnam_xml = '''
            <body>
            <items>
                <item>
                    <statsYm>202301</statsYm>
                    <mvinAdmmCd>1128000000</mvinAdmmCd>
                    <mvtAdmmCd>1114000000</mvtAdmmCd>
                    <mvinCtpvNm>서울특별시</mvinCtpvNm>
                    <mvtCtpvNm>서울특별시</mvtCtpvNm>
                    <mvinSggNm>광진구</mvinSggNm>
                    <mvtSggNm>강남구</mvtSggNm>
                    <totNmprCnt>60</totNmprCnt>
                    <maleNmprCnt>32</maleNmprCnt>
                    <femlNmprCnt>28</femlNmprCnt>
                </item>
            </items>
        </body>
    '''
    gwangjingu_gangnam_response = create_mock_response(gwangjingu_gangnam_xml)

    gwangjingu_gwangjingu_xml = '''
        <body>
            <items>
                <item>
                    <statsYm>202301</statsYm>
                    <mvinAdmmCd>1128000000</mvinAdmmCd>
                    <mvtAdmmCd>1128000000</mvtAdmmCd>
                    <mvinCtpvNm>서울특별시</mvinCtpvNm>
                    <mvtCtpvNm>서울특별시</mvtCtpvNm>
                    <mvinSggNm>광진구</mvinSggNm>
                    <mvtSggNm>광진구</mvtSggNm>
                    <totNmprCnt>90</totNmprCnt>
                    <maleNmprCnt>48</maleNmprCnt>
                    <femlNmprCnt>42</femlNmprCnt>
                </item>
            </items>
        </body>

    '''
    gwangjingu_gwangjingu_response = create_mock_response(gwangjingu_gwangjingu_xml)

    mock_districts = {
        "강남구":"1114000000",
        "광진구":"1128000000"
    }


    mock_get.side_effect = [
        gangnam_gangnam_response,
        gangnam_gwangjingu_response,
        gwangjingu_gangnam_response,
        gwangjingu_gwangjingu_response
    ]

    start = "202301"
    end = "202303"

    result = get_population_flow(
        mock_districts,
        start,
        end
    )

    assert mock_get.call_count == 4
    assert len(result) == 4
    assert result.iloc[0]["date"] == "202301"
    assert result.iloc[0]["total_people"] == "110"