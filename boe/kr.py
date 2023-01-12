import pandas as pd
import boe

def get_bank_rate(start_date: pd.Timestamp = pd.Timestamp(1900, 1, 1),
                         end_date:pd.Timestamp = None) -> pd.Series:
    """
    Get Bank of England main refinancing operations key rate monthly time series.
    """
    start_period = start_date.strftime("%Y-%m-%d")
    end_period = None if end_date is None else end_date.strftime("%Y-%m-%d")
    s = boe.request_data.get_data_frame()
    s.rename("bank_rate", inplace=True)
    return s / 100
