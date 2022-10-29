import pandas as pd
import requests
from io import StringIO

from requests import Response

URL_BASE = "https://www.bankofengland.co.uk/boeapps/database/Bank-Rate.asp"



def get_data_frame(
    start_period: str = "1900-01-01",
    end_period: str = None,
) -> pd.Series:
    request_url = URL_BASE
    try:
        abc: Response = requests.get(request_url)
    except requests.exceptions.HTTPError as err:
        raise requests.exceptions.HTTPError(
            f"HTTP error fetching data for {URL_BASE}:",
            abc.status_code,
            abc.reason,
            URL_BASE,
        ) from err
    jresp = abc.text
    df = pd.read_table(StringIO(jresp))

    af = 1

    return 1
