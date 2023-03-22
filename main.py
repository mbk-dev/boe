import pandas as pd
import boe

val = boe.kr.get_bank_rate(start_date=pd.Timestamp(2022, 1, 1))
print(val)

print(boe.__version__)
