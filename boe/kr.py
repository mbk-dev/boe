import pandas as pd
import boe

def get_bank_rate() -> pd.Series:
    """
    Get Bank of England main refinancing operations key rate monthly time series.
    """
    s = boe.request_data.get_data_frame()
    s.rename("bank_rate", inplace=True)
    return s / 100
