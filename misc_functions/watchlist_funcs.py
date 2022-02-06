import requests
import pandas as pd
import numpy as np
from global_vars import *

# functions
def watchlist_get_overview():
    url = 'https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=250&page=1&sparkline=false'
    client = requests.Session()
    r = client.get(url)
    results = []
    for json_line in r.json():
        if json_line['symbol'] in COIN_WATCHLIST_GECKO_SYMBOL:
            results.append(json_line)
    
    results = pd.DataFrame(results)[['name','symbol', 'current_price', 'market_cap','market_cap_rank', 'total_volume','high_24h', 'low_24h','price_change_percentage_24h','market_cap_change_percentage_24h', 'circulating_supply','total_supply', 'ath', 'ath_change_percentage','ath_date']]
    results.rename(columns={
        'market_cap_change_percentage_24h':'markcap_%_change_24h'
        ,'ath_change_percentage':'ath_%_change'
        ,'price_change_percentage_24h':'price_%_change_24h'
        ,'total_volume':'tot_vol'
        ,'market_cap_rank':'markcap_rank'
        ,'market_cap':'markcap'
    },inplace=True)
    return results
