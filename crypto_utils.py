import numpy as np
import requests
import itertools
from portfolio_keys import CURRENCY_API_KEY
from global_vars import PAIRS
def _init_currency_conversion_rates():
    url = "https://free.currconv.com/api/v7/convert?"
    conversion_rates = {'USDT':1,'BUSD':1,'USD':1} # need to dynamic update this via api call 
    currency_b = ['EUR_USD','GBP_USD']
    for c in currency_b:
        params = {'q':c,'compact':'ultra','apiKey':CURRENCY_API_KEY}
        conversion_rates[c.split('_')[0]]= np.float64(list(requests.get(url,params=params).json().values()))[0]
    
    return conversion_rates


def _paring_returner(symbol=None,exchange=None):
    
    if symbol==None:
        return list(itertools.chain.from_iterable(PAIRS[exchange].values()))
    return PAIRS[exchange][symbol]

def _price_coverter(pair_base,currency_denominated_value):
    
    #conversion_rates = {'GBP':1.34,'USDT':1,'BUSD':1,'EUR':1.11} # need to dynamic update this via api call 
    conversion_rates = CONVERSION_RATES
    
    if pair_base=='GBPUSDT':
        return currency_denominated_value
    
    currencies = ['GBP','USDT','EUR','BUSD']    
    currency = [currency for currency in currencies if currency in pair_base][0]

    returned_usd_equivalent = currency_denominated_value * conversion_rates[currency]
    return returned_usd_equivalent

CONVERSION_RATES = _init_currency_conversion_rates()

def _binance_price_coverter___(pair_base,currency_denominated_value):
    
    url = "https://free.currconv.com/api/v7/convert?"
    conversion_rates = {'USDT':1,'BUSD':1,'USD':1} # need to dynamic update this via api call 
    currency_b = ['EUR_USD','GBP_USD']
    for c in currency_b:
        params = {'q':c,'compact':'ultra','apiKey':CURRENCY_API_KEY}
        conversion_rates[c.split('_')[0]]= np.float64(list(requests.get(url,params=params).json().values()))
    
    if pair_base=='GBPUSDT':
        return currency_denominated_value
    
    currencies = ['GBP','USDT','EUR','BUSD','USD']
    currency = [currency for currency in currencies if currency in pair_base][0]
    
    returned_usd_equivalent = currency_denominated_value * conversion_rates[currency]
    return returned_usd_equivalent
