import requests
import pandas as pd
from datetime import datetime
import datetime
import os
import time
import urllib.parse
import hashlib
import hmac
import base64
from binance.spot import Spot
from portfolio_keys import *


user_agent = 'crypto_palantir'
Binanceclient = Spot(key=BINANCE_API_KEY, secret=BINANCE_PRIVATE_KEY)
#Krakenclient = KrakenAPI()
#r = Krakenclient.query_public('Ticker',params={'pair': 'BTCUSDT'})

class KrakenAPI(object):
    
    
    def __init__(self, key='', secret=''):

        self.key = os.getenv('KRAKEN_API_KEY')
        self.secret = os.getenv('KRAKEN_PRIVATE_KEY')
        self.base_url = 'https://api.kraken.com'
        self.apiversion = '0'
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': user_agent})
        self.response = None
        self.history = []
        return


    def _allowed_endpoints(self,endpoint_call):
        
        api_endpoints = {
            'PRIVATE' : ['TradeBalance','Balance','OpenOrders','ClosedOrders','QueryOrders','TradeHistory','OpenPositions']
            ,'PUBLIC' : ['','']
        }
        return True if endpoint_call in api_endpoints['XXXX'] else False
    
    
    
    def _sign(self, data, urlpath):
        
        """ 
        Each request needs to be made with a signed API request
        # See more: https://docs.kraken.com/rest/#section/Authentication/Headers-and-Signature

        :data: API request parameters. {type: dict}
        :urlpath: API URL path sans host {type: str}
        :returns: signature digest
        """
        
        postdata = urllib.parse.urlencode(data)

        # Unicode-objects must be encoded before hashing
        encoded = (str(data['nonce']) + postdata).encode()
        message = urlpath.encode() + hashlib.sha256(encoded).digest()

        signature = hmac.new(base64.b64decode(self.secret), message, hashlib.sha512)
        sigdigest = base64.b64encode(signature.digest())

        return sigdigest.decode()
    
    
    
    def query_public(self, endpoint_call, params=None, timeout=None):
        """ Performs an API query that does not require a valid key/secret pair.
        
        For Public end points, consult: https://docs.kraken.com/rest/#tag/Market-Data
        :param endpoint_call: API endpoint_call name {type:str}
        :param data: (optional) API request parameters {type:dict}
        :param timeout: (optional) if not ``None``, a :py:exc:`requests.HTTPError`
                        will be thrown after ``timeout`` seconds if a response
                        has not been received
        :type timeout: int or float
        :returns: parsed json response

        """
        params = {} if params is None else params
        
        full_url = self.base_url + '/' + self.apiversion + '/public/' + endpoint_call
        
        self.response = self.session.get(full_url,params=params)
        if len(self.response.json()['error'])>0:
            return self.response.json()['error'][0]
        
        self.history.append({endpoint_call:self.response.json()}) 
        return self.response.json()


    
    def query_private(self, endpoint_call, data=None, timeout=None):
        """ Performs an API query that requires a valid key/secret pair.

        :param endpoint_call: API endpoint_call name
        :type endpoint_call: str
        :param data: (optional) API request parameters
        :type data: dict
        :param timeout: (optional) if not ``None``, a :py:exc:`requests.HTTPError`
                        will be thrown after ``timeout`` seconds if a response
                        has not been received
        :type timeout: int or float
        :returns: :py:meth:`requests.Response.json`-deserialised Python object

        """
        data = {} if data is None else data


        data['nonce'] = int(1000*time.time())

        urlpath = '/' + self.apiversion + '/private/' + endpoint_call
    
        headers = {'API-Key': self.key,'API-Sign': self._sign(data, urlpath)}
        
        full_url = self.base_url + urlpath

        self.response = self.session.post(full_url, data = data, headers = headers,timeout = timeout)
        
        if len(self.response.json()['error'])>0:
            return self.response.json()['error'][0]
        
        self.history.append({endpoint_call:self.response.json()}) 
        
        
        return self.response.json()
    
Krakenclient = KrakenAPI()
