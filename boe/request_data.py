import pandas as pd
import requests
from io import StringIO

from requests import Response

URL_BASE = "https://www.bankofengland.co.uk/boeapps/database/Bank-Rate.asp#"



def get_data_frame(
        freq: str = "D",
        start_period: str = "1900-01-01",
        end_period: str = None,
) -> pd.Series:
    request_url = URL_BASE
    resp = requests.get(request_url)
    while ( not (resp.status_code == 200)):
        resp = requests.get(request_url)
    try:
        abc: Response = requests.get(request_url,cookies=resp.cookies)
    except requests.exceptions.HTTPError as err:
        raise requests.exceptions.HTTPError(
            f"HTTP error fetching data for {URL_BASE}:",
            abc.status_code,
            abc.reason,
            URL_BASE,
        ) from err
    jresp = abc.text
    df = pd.read_html(StringIO(jresp))
    df = df[0]

    df.rename(columns={df.columns[0]: "date"}, inplace=True)
    df['date'] = pd.to_datetime(df['date'], format='%d %b %y')
    df.set_index("date", inplace=True)
    df.index = df.index.to_period(freq=freq)
    return df.squeeze()
