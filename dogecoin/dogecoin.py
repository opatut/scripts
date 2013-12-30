#!/usr/bin/env python3

import requests, json

dogeval = requests.get("http://doge.yottabyte.nu/ajax/lastval.php").json()
btcval = requests.get("http://data.mtgox.com/api/1/BTCUSD/ticker").json()

btc_per_doge = float(dogeval["val"])
usd_per_btc = float(btcval["return"]["last"]["value"])
usd_per_doge = usd_per_btc * btc_per_doge
doge_per_usd = 1 / usd_per_doge

# print("%22.11f BTC / DOGE"%btc_per_doge)
# print("%22.11f USD / BTC "%usd_per_btc)
# print("%22.11f USD / DOGE"%usd_per_doge)
# print("%22.11f DOGE / USD"%doge_per_usd)
print("%6.2f"%doge_per_usd)
