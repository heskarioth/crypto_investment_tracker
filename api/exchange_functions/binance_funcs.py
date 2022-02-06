import pandas as pd
import numpy as np
import itertools 
#from sqlalchemy import create_engine
#import sqlalchemy
import requests 

from binance.spot import Spot 
from datetime import datetime
from crypto_utils import _paring_returner,_price_coverter
from portfolio_keys import BINANCE_API_KEY,BINANCE_PRIVATE_KEY
from misc_functions.common_functions import generic_dca_profit_loss, database_recon_update

Binanceclient = Spot(key=BINANCE_API_KEY, secret=BINANCE_PRIVATE_KEY)



# get our open orders
def binance_get_open_orders(object):
    orders = object.get_open_orders() 
    df_open_orders = pd.DataFrame()
    for json_line in orders:
        df_open_orders = pd.concat([df_open_orders,pd.DataFrame({
            'pair':json_line['symbol']
            ,'vol':json_line['origQty']
            ,'price':json_line['price']
            ,'type':json_line['side']
            ,'open_time': datetime.fromtimestamp((int(json_line['time'] / 1000))).strftime("%A, %d %B %Y, %H:%M:%S.%f")
            ,'order': '{} {} {} @ {} {}'.format(json_line['side'],json_line['origQty'],json_line['symbol'],json_line['type'],json_line['price'])
        },index=[0])])
    
    df_open_orders['exchange'] = 'binance'
    return df_open_orders.reset_index(drop=True)



# get all account trades
def binance_get_all_trades(object,symbols=None,dca=False):
    
    trades_history_current = pd.DataFrame() 
    
    if symbols==None:
        symbols = _paring_returner(None,exchange='BINANCE')
        
    for symbol in symbols:
        
        orders = object.get_orders(**{'symbol':symbol,'limit':1000})
        
        for idx in range(len(orders)):
            trades_history_current = pd.concat([trades_history_current,pd.DataFrame({'symbol': str(orders[idx]['symbol'])
             , 'orderId': orders[idx]['orderId']
             , 'orderListId': orders[idx]['orderListId']
             , 'clientOrderId': orders[idx]['clientOrderId']
             , 'price': np.float64(orders[idx]['price'])
             , 'origQty': np.float64(orders[idx]['origQty'])
             , 'executedQty': np.float64(orders[idx]['executedQty'])
             , 'cummulativeQuoteQty': np.float64(orders[idx]['cummulativeQuoteQty'])
             , 'status': str(orders[idx]['status'])
             , 'type': str(orders[idx]['type'])
             , 'side': str(orders[idx]['side'])                                              
            ,'time_str':datetime.fromtimestamp((int(orders[idx]['time'] / 1000))).strftime("%A, %d %B %Y, %H:%M:%S.%f")
            ,'time_t':pd.to_datetime(datetime.fromtimestamp((int(orders[idx]['time'] / 1000))).strftime("%A, %d %B %Y, %H:%M:%S.%f"))
            ,'time_epoch':int(orders[idx]['time'] / 1000)
            ,'updateTime_str':datetime.fromtimestamp((int(orders[idx]['updateTime'] / 1000))).strftime("%A, %d %B %Y, %H:%M:%S.%f")
            ,'updateTime_t':pd.to_datetime(datetime.fromtimestamp((int(orders[idx]['updateTime'] / 1000))).strftime("%A, %d %B %Y, %H:%M:%S.%f"))
            ,'updateTime_epoch':int(orders[idx]['updateTime'] / 1000)                                                               
             , 'isWorking': bool(orders[idx]['isWorking'])
             , 'origQuoteOrderQty': np.float64(orders[idx]['origQuoteOrderQty'])
            },index=[0])])
    
    trades_history_current.drop_duplicates(subset=['orderId'],keep=False, inplace=True)
    
    df_recon = database_recon_update(trades_history_current,tb_name='binance_trades_history',unique_identifier='orderId')
    
    pattern = '|'.join(['USDT', 'GBP','BUSD'])
    df_recon['filter'] = df_recon.symbol.str.replace(pattern,'',regex=True)
    
    return df_recon[['symbol', 'price', 'origQty','executedQty', 'cummulativeQuoteQty','side','time_str','orderId', 'orderListId', 'clientOrderId', 'status', 'type','time_t', 'time_epoch', 'updateTime_str', 'updateTime_t','updateTime_epoch', 'isWorking', 'origQuoteOrderQty','filter']].reset_index(drop=True)



# get past dividends
def binance_get_past_dividends(object):
    
    _, savings_account = binance_get_savings(object,None)
    interest_paying_coins = list(savings_account.asset)
    
    df_dividends_current = pd.DataFrame()

    for coin in interest_paying_coins:

        response = (object.asset_dividend_record(**{'limit':500,'asset':coin})['rows'])

        for idx in range(len(response)):

            df_dividends_current = pd.concat([df_dividends_current,pd.DataFrame({
                'id':response[idx]['id']
                ,'tranId':response[idx]['tranId']
                ,'asset':response[idx]['asset']
                ,'amount':np.float64(response[idx]['amount'])
                ,'divTime_str':datetime.fromtimestamp((int(response[idx]['divTime'] / 1000))).strftime("%A, %d %B %Y, %H:%M:%S.%f")
                ,'divTime_t':pd.to_datetime(datetime.fromtimestamp((int(response[idx]['divTime'] / 1000))).strftime("%A, %d %B %Y, %H:%M:%S.%f"))
                ,'divTime_epoch':int(response[idx]['divTime'] / 1000)
                ,'enInfo':str(response[idx]['enInfo'])},index=[0])])
    
    df_recon = database_recon_update(df_dividends_current,tb_name='binance_interest_history',unique_identifier='tranId')
        
    return df_recon


#get all tokens
def binance_get_wallet(object):
    
    wallet = (object.account())
    wallet = pd.DataFrame(wallet['balances'])
    wallet['free'] = wallet['free'].astype(np.float64)
    wallet['locked'] = wallet['locked'].astype(np.float64)
    wallet.drop('locked',axis=1,inplace=True)
    wallet  = wallet[wallet['free']>0]
    wallet['currently_on_lending']= wallet.asset.str.contains('LD')
    wallet = wallet[~wallet.asset.isin(['LRC', 'TRX', 'XVG', 'EON', 'ADD', 'MEETONE', 'ATD', 'EOP', 'IQ', 'WIN', 'JST', 'BTTC'])].rename(columns={'free':'amount'})
    return wallet

# get available coins. This will return all coins not in lending
def binance_get_available_coins(object):
    
    list_of_coins = ['ADA','BTC','GBP','AAVE','USDT','ETH','XLM','HBAR','BNB','EOS','USDC','TRX','MATIC','STX']
    indices = []
    df_coins = pd.DataFrame()
    
    coin_info = object.coin_info()

    for idx in range(len(coin_info)):
        #get our coins
        if coin_info[idx]['coin'] in list_of_coins:
            indices.append(idx)

    #add them to a dataframe
    for idx in indices:
        df_coins = pd.concat([df_coins,pd.DataFrame(coin_info[idx])])

    df_coins.reset_index(drop=True,inplace=True)
    df_coins['good_record'] = False
    for idx in range(df_coins.shape[0]):
        if df_coins['networkList'].iloc[idx]['network'] in ['BNB','FIAT_MONEY','XLM','HBAR']:
            df_coins.loc[idx,'good_record'] = True
    df_coins = df_coins[df_coins['good_record']==True].drop('good_record',axis=1)
    
    return df_coins
    

#get tokens in savings account. This will return all tokens in lending.
def binance_get_savings(object,binance_interest_history):
    savings_account = object.savings_account()
    savings_df = pd.DataFrame(savings_account['positionAmountVos'])
    if isinstance(binance_interest_history,pd.DataFrame):
        accrued_interest = binance_interest_history.groupby(['asset'])['amount'].sum().to_dict()
        savings_df['accrued_interest'] = savings_df['asset'].map(accrued_interest)
        
    total_savings_balances = {'balance_inBTC':savings_account['totalAmountInBTC'],'balance_inUSDT':savings_account['totalAmountInUSDT']}
    return total_savings_balances,savings_df


def binance_get_historical_interest(object,n_days=120):
    df_savings_history = pd.DataFrame()
    offset = 86400000
    end_date= int(datetime.timestamp((datetime.today().replace(microsecond=0)))) * 1000
    
    for i in range(n_days):
        start_date = end_date - offset
        savings_history = object.savings_interest_history(lendingType='DAILY',**{'startTime':start_date,'endTime':end_date})
        for idx in range(len(savings_history)):
            df_savings_history = pd.concat([df_savings_history,pd.DataFrame(
              {'createTime': datetime.fromtimestamp((int(savings_history[idx]['time'] / 1000))).strftime("%A, %d %B %Y, %H:%M:%S.%f")
             , 'productName': savings_history[idx]['productName'] 
             , 'asset': savings_history[idx]['asset'] 
             , 'interest': np.float64(savings_history[idx]['interest'] )
             , 'lendingType': savings_history[idx]['lendingType']},index=[0])])
    
    return df_savings_history.reset_index(drop=True)

def binance_get_deposit_history(object,start_date=None):
    #1612281765000 === 02.02.2021
    start_date = 1612281765000 if start_date == None else start_date
    
    # get me all deposits from given start date
    stop_date= int(datetime.timestamp((datetime.today().replace(microsecond=0)))) * 1000
    #start_date = 1612281765000 # 02.02.2021
    n_days = 20
    end_date = start_date + (86400000 * n_days)
    results = []
    # asynch call here
    while end_date<stop_date:
        start_date = end_date
        end_date = end_date + (86400000 * n_days)
        results.append(object.fiat_order_history(transactionType=0,**{'startTime':start_date,'endTime':end_date}))
    
    # parse results and return dataframe
    df_deposit = pd.DataFrame()
    for idx in range(len(results)):
        if len(results[idx]['data'])>0:
            for json_line in results[idx]['data']:
                df_deposit = pd.concat([df_deposit,pd.DataFrame({
                'fiatCurrency': json_line['fiatCurrency']
                ,'indicatedAmount': np.float64(json_line['indicatedAmount'])
                ,'amount': np.float64(json_line['amount'])
                ,'totalFee': np.float64(json_line['totalFee'])
                ,'method': str(json_line['method'])
                ,'status': str(json_line['status'])
                ,'createTime_epoch': np.float64(json_line['createTime'])
                ,'createTime_timestamp': datetime.fromtimestamp((int(json_line['createTime'] / 1000))).strftime("%A, %d %B %Y, %H:%M:%S.%f")
                ,'updateTime_epoch': np.float64(json_line['updateTime'])
                ,'updateTime_timestamp': datetime.fromtimestamp((int(json_line['updateTime'] / 1000))).strftime("%A, %d %B %Y, %H:%M:%S.%f")
                ,'orderNo':json_line['orderNo']
                        },index=[json_line['orderNo']])])
     
    df_deposit['usd_base_price'] = df_deposit.apply(lambda x: _price_coverter(x['fiatCurrency'],x['indicatedAmount']),axis=1)
    df_deposit['exchange'] = 'binance'
    return df_deposit


def binance_get_spot_balance(object):
    snap = object.account_snapshot(type='SPOT')
    spotbalance = pd.DataFrame({
        'balance_inBTC': np.float64(snap['snapshotVos'][0]['data']['totalAssetOfBtc'])
        ,'balance_inUSDT': np.float64(object.avg_price(**{'symbol':'BTCUSDT'})['price']) * np.float64(snap['snapshotVos'][0]['data']['totalAssetOfBtc'])
                   },index=[0]).T
    return spotbalance.reset_index()


def binance_get_total_account_size(object):
    
    binance_spot = binance_get_spot_balance(object)
    binance_savings = binance_get_savings(object,None)
    account_size = (pd.concat([pd.DataFrame(binance_savings[0],index=[0]).T.reset_index(),binance_spot])
 .set_index('index')
 .astype(np.float64)
 .groupby(level=0).sum().reset_index())
    return account_size


def binance_dca_profit_loss(object):
    df_trades = binance_get_all_trades(object)
    df_trades = df_trades[df_trades['cummulativeQuoteQty']>0]
    df_trades = df_trades[['time_t','time_epoch','side','symbol','price','cummulativeQuoteQty','isWorking','executedQty','clientOrderId','filter']]
    df_trades.columns = ['timestamp_t', 'timestamp_epoch', 'type', 'pair', 'asset_market_price','operation_cost', 'isWorking', 'crypto_vol', 'transaction_id', 'filter']
    binance_dca_df = generic_dca_profit_loss(object,df_trades,exchange='BINANCE')
    return binance_dca_df.reset_index(drop=True)
