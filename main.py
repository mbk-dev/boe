import boe

val = boe.kr.get_bank_rate()
#val = val.pct_change().round(4)
print(val)

print(boe.__version__)
