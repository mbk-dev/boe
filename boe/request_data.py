import pandas as pd
import requests
from io import StringIO

from requests import Response

URL_BASE = "https://www.bankofengland.co.uk/boeapps/database/Bank-Rate.asp#"

headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.90 Safari/537.36'}

def get_data_frame(
        freq: str = "D",
        start_period: str = "1900-01-01",
        end_period: str = None,
) -> pd.Series:
    request_url = URL_BASE

    try:
        abc: Response = requests.get(request_url, headers=headers)
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
    # The Bank-Rate table is served newest-first. Sort ascending BEFORE slicing
    # and padding: on a descending index label slices invert their meaning, and
    # reindex(method='pad') fills each day from the NEXT (future) rate change
    # instead of the previous one - a look-ahead that made every value between
    # two changes wrong.
    df.sort_index(inplace=True)
    df.index = df.index.to_period(freq=freq)
    # Pad over the FULL change-dates table first, then slice: slicing the raw
    # change dates by start_period would drop the change that is still in
    # effect at start_period (a window opening between two changes would lose
    # the standing rate, or come back empty). Pad through today - the standing
    # rate stays in effect after the last change.
    today = pd.Timestamp.today().to_period(freq)
    idx = pd.period_range(start=df.index[0], end=max(df.index[-1], today), freq=freq)
    df = df.reindex(idx, method='pad')
    df = df.loc[pd.Period(start_period, freq=freq):]
    if end_period is not None:
        df = df.loc[:pd.Period(end_period, freq=freq)]
    return df.squeeze(axis=1)
