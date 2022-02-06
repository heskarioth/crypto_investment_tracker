
import pandas as pd
import numpy as np
from datetime import datetime

from binance.spot import Spot

from portfolio_keys import *
from misc_functions.common_functions import generic_dca_profit_loss, database_recon_update
from crypto_utils import _paring_returner,_price_coverter

Binanceclient = Spot(key=BINANCE_API_KEY, secret=BINANCE_PRIVATE_KEY)
# help functions for final report
def kraken_get_balance_deprecated(object):
    
    return pd.DataFrame(object.query_private('Balance')['result'],index=[0])

def kraken_get_open_orders(object):
    orders = object.query_private('OpenOrders')
    df_orders = pd.DataFrame()
    for order in orders['result']['open'].keys():
        df_orders = pd.concat([df_orders,pd.DataFrame({
            'open_time':datetime.fromtimestamp(orders['result']['open'][order]['opentm']).strftime("%A, %d %B %Y, %H:%M:%S")
            ,'pair': orders['result']['open'][order]['descr']['pair']
            ,'ordertype': orders['result']['open'][order]['descr']['ordertype']
            ,'type': orders['result']['open'][order]['descr']['type']
            ,'price': orders['result']['open'][order]['descr']['price']
            ,'vol':orders['result']['open'][order]['vol']
            ,'order': orders['result']['open'][order]['descr']['order']
            ,'fee':orders['result']['open'][order]['fee']

            ,'transaction_id' : order
        },index=[order])])
    
    df_orders['exchange'] = 'kraken'
    return df_orders

def kraken_get_transactions_history_deprecated(object):
    tradeshistory = object.query_private('TradesHistory')
    df_tradeshistory = pd.DataFrame()
    for trade in tradeshistory['result']['trades']:
        df_tradeshistory = pd.concat([df_tradeshistory,pd.DataFrame({
                'timestamp_str':datetime.fromtimestamp(tradeshistory['result']['trades'][trade]['time']).strftime("%A, %d %B %Y, %H:%M:%S.%f")
                ,'timestamp_t':pd.to_datetime(datetime.fromtimestamp(tradeshistory['result']['trades'][trade]['time']).strftime("%A, %d %B %Y, %H:%M:%S.%f"))
                ,'timestamp_epoch':tradeshistory['result']['trades'][trade]['time']
                ,'ordertxid': str(tradeshistory['result']['trades'][trade]['ordertxid'])
                ,'postxid': str(tradeshistory['result']['trades'][trade]['postxid'])
                ,'type': str(tradeshistory['result']['trades'][trade]['type'])
                ,'pair': str(tradeshistory['result']['trades'][trade]['pair'])
                ,'asset_market_price': np.float64(tradeshistory['result']['trades'][trade]['price'])
                ,'operation_cost': np.float64(tradeshistory['result']['trades'][trade]['cost'])
                ,'fee': np.float64(tradeshistory['result']['trades'][trade]['fee'])
                ,'crypto_vol': np.float64(tradeshistory['result']['trades'][trade]['vol'])
                ,'margin': np.float64(tradeshistory['result']['trades'][trade]['margin'])
                ,'transaction_id' : trade
            },index=[trade])])
    return df_tradeshistory



def kraken_get_ledger_info(object):
    
    ledger = object.query_private('Ledgers')
    df_ledger = pd.DataFrame()
    for ledger_entry in ledger['result']['ledger'].keys():
            df_ledger = pd.concat([df_ledger,pd.DataFrame({
                'timestamp_str':datetime.fromtimestamp(ledger['result']['ledger'][ledger_entry]['time']).strftime("%A, %d %B %Y, %H:%M:%S.%f")
                ,'timestamp_t':pd.to_datetime(datetime.fromtimestamp(ledger['result']['ledger'][ledger_entry]['time']).strftime("%A, %d %B %Y, %H:%M:%S.%f"))
                ,'timestamp_epoch':ledger['result']['ledger'][ledger_entry]['time']
                ,'ref_id': str(ledger['result']['ledger'][ledger_entry]['refid'])
                ,'type': str(ledger['result']['ledger'][ledger_entry]['type'])
                ,'asset': str(ledger['result']['ledger'][ledger_entry]['asset'])
                ,'amount': np.float64(ledger['result']['ledger'][ledger_entry]['amount'])
                ,'fee': np.float64(ledger['result']['ledger'][ledger_entry]['fee'])
                ,'transaction_id' : ledger_entry
            },index=[ledger_entry])])
    return df_ledger
    
    

def kraken_get_total_account_size(object):
    
    spot_balance = kraken_get_spot_balance(object)
    savings_balance,_= kraken_get_savings(object)
    
    return pd.concat([spot_balance,savings_balance]).reset_index().groupby('index').sum().reset_index()



def kraken_get_interest_history(object):
    
    interest_history_current = kraken_get_ledger_info(object)
    interest_history_current= interest_history_current[interest_history_current.type=='staking']

    df_recon = database_recon_update(interest_history_current,tb_name='kraken_interest_history',unique_identifier='transaction_id')
    df_recon.asset = df_recon.asset.str.replace('.S','',regex=True) # for filter button
    
    return df_recon


def kraken_get_balance(object):
    df_balance = pd.DataFrame(object.query_private('Balance')['result'],index=[0]).reset_index(drop=True).T.reset_index().rename(columns={'index':'asset',0:'quantity'})
    df_balance['is_staked'] = False
    for idx in range(df_balance.shape[0]):
        if '.S' in df_balance.iloc[idx]['asset']:
            df_balance.loc[idx,'is_staked'] =True
            
    df_balance.quantity = df_balance.quantity.astype(np.float64)
    return df_balance


def kraken_get_savings(object):
    df_balance = kraken_get_balance(object)
    
    df_savings = df_balance[df_balance.is_staked==True].reset_index(drop=True).copy()
    df_savings['asset'].str.replace('.S','',regex=True).to_list()
    df_savings['balance_inBTC'] = 0 
    df_savings['balance_inUSDT'] =0
    for idx in range(df_savings.shape[0]):
        asset_n =df_savings['asset'].iloc[idx].replace('.S','')
        df_savings.loc[idx,'asset'] = df_savings.loc[idx,'asset'].replace('.S','')
        df_savings.loc[idx,'balance_inUSDT'] = (np.float(df_savings['quantity'].iloc[idx])*np.float64(Binanceclient.avg_price('{}USDT'.format(asset_n))['price']))
        df_savings.loc[idx,'balance_inBTC'] = (np.float(df_savings['quantity'].iloc[idx])*np.float64(Binanceclient.avg_price('{}BTC'.format(asset_n))['price']))
    
    savings_overview = pd.DataFrame(df_savings[['balance_inBTC','balance_inUSDT']].sum())
    return savings_overview,df_savings[['asset', 'quantity', 'balance_inBTC', 'balance_inUSDT']]

def kraken_price_converter(base,quantity):
    # helper function for kraken_get_spot_balance and summary_get_deposits
    asset_parsed = {'ZEUR':'EUR','USDC':'USD','ZUSD':'USD','GBP':'GBP'}
    base = asset_parsed[base]
    conversion_rates = {'GBP':1.34,'USDT':1,'BUSD':1,'EUR':1.13,'USD':1} # need to dynamic update this via api call 
    usd_base_price = conversion_rates[base] * quantity
    return usd_base_price
    
def kraken_get_spot_balance(object):
    
    wallet = kraken_get_balance(object)
    
    FIAT_CURRENCY = ['ZEUR','USDC','ZUSD','ZGBP']
    
    #get fiat balance
    fiat_df = wallet[(wallet.is_staked==False) & (wallet.quantity>0) & (wallet.asset.isin(FIAT_CURRENCY))].reset_index(drop=True)
    fiat_df['usd_base_price'] = fiat_df.apply(lambda x: kraken_price_converter(x['asset'],x['quantity']),axis=1)
    
    spot_balance = pd.DataFrame({
        'balance_inUSDT':np.float64(fiat_df.usd_base_price.sum())
      ,'balance_inBTC': np.float64(fiat_df.usd_base_price.sum()) / np.float(Binanceclient.avg_price(**{'symbol':'BTCUSDT'})['price'])
                            },index=[0]).T
    
    return spot_balance


def kraken_get_transactions_history(object):
    tradeshistory = object.query_private('TradesHistory')
    trades_history_current = pd.DataFrame()
    for trade in tradeshistory['result']['trades']:
        trades_history_current = pd.concat([trades_history_current,pd.DataFrame({
                'timestamp_str':datetime.fromtimestamp(tradeshistory['result']['trades'][trade]['time']).strftime("%A, %d %B %Y, %H:%M:%S.%f")
                ,'timestamp_t':pd.to_datetime(datetime.fromtimestamp(tradeshistory['result']['trades'][trade]['time']).strftime("%A, %d %B %Y, %H:%M:%S.%f"))
                ,'timestamp_epoch':tradeshistory['result']['trades'][trade]['time']
                ,'ordertxid': str(tradeshistory['result']['trades'][trade]['ordertxid'])
                ,'postxid': str(tradeshistory['result']['trades'][trade]['postxid'])
                ,'type': str(tradeshistory['result']['trades'][trade]['type'])
                ,'pair': str(tradeshistory['result']['trades'][trade]['pair'])
                ,'asset_market_price': np.float64(tradeshistory['result']['trades'][trade]['price'])
                ,'operation_cost': np.float64(tradeshistory['result']['trades'][trade]['cost'])
                ,'fee': np.float64(tradeshistory['result']['trades'][trade]['fee'])
                ,'crypto_vol': np.float64(tradeshistory['result']['trades'][trade]['vol'])
                ,'margin': np.float64(tradeshistory['result']['trades'][trade]['margin'])
                ,'transaction_id' : trade
            },index=[trade])])
    
    
    df_recon = database_recon_update(trades_history_current,tb_name='kraken_trades_history',unique_identifier='transaction_id')
    
    pattern = '|'.join(['USDT', 'GBP','BUSD','EUR','ZEURZ'])
    df_recon['filter'] = df_recon.pair.str.replace(pattern,'',regex=True)
    
    return df_recon[['timestamp_t', 'timestamp_epoch','type', 'pair', 'asset_market_price', 'operation_cost','fee', 'crypto_vol', 'transaction_id','filter']].sort_values(by=['timestamp_epoch'],ascending=False).reset_index(drop=True)



def kraken_get_deposit_history(object):
    df_deposit = kraken_get_ledger_info(object)
    df_deposit = df_deposit[df_deposit.type=='deposit']
    df_deposit['usd_base_price'] = df_deposit.apply(lambda x: kraken_price_converter(x['asset'],x['amount']),axis=1)
    df_deposit['exchange'] = 'kraken'
    return df_deposit

def kraken_dca_profit_loss(object):
    df_trades = kraken_get_transactions_history(object)
    # Convert all trading pairs to dollar denominated equivalent. E.g. BTCGBP --> BTCUSDT
    #df_trades['usd_base_price'] = df_trades.apply(lambda x: _price_coverter(x['pair'],x['operation_cost']),axis=1)
    kraken_dca_df = generic_dca_profit_loss(object,df_trades,exchange='KRAKEN')
    
    return kraken_dca_df.reset_index(drop=True)
