
import pandas as pd
import numpy as np
from datetime import datetime
import collections


from binance.spot import Spot
from portfolio_keys import * 
from crypto_utils import _paring_returner,_price_coverter

Binanceclient = Spot(key=BINANCE_API_KEY, secret=BINANCE_PRIVATE_KEY)

def summary_get_overview_tab(kraken_df,binance_df):
    
    #get asset pricing pair dollar denominated
    assets_current_price = pd.concat([kraken_df,binance_df]).drop_duplicates(subset='symbol').set_index('symbol')['current_trading_price'].to_dict()
    #combine binance and kraken numbers
    df_portfolio_overview = pd.concat([kraken_df,binance_df]).groupby(['symbol'])['total_qt','total_price_paid'].apply(sum).reset_index().copy()
    #calculate dca
    df_portfolio_overview['dca'] =  np.float64(df_portfolio_overview['total_price_paid']/df_portfolio_overview['total_qt'])
    #map each asset per its current price
    df_portfolio_overview['current_price'] = np.float64(df_portfolio_overview['symbol'].map(assets_current_price))
    #calculate current market value of the asset you own
    df_portfolio_overview['current_market_value']= np.float64(df_portfolio_overview['current_price'] * df_portfolio_overview['total_qt'])
    #calculate profit
    df_portfolio_overview['profit_loss'] =  np.float64((df_portfolio_overview['current_price'] * df_portfolio_overview['total_qt'])- df_portfolio_overview['total_price_paid'])
    #calculate percentage profit / loss
    df_portfolio_overview['percentage_change'] = np.float64(((df_portfolio_overview['current_price']*df_portfolio_overview['total_qt'])-df_portfolio_overview['total_price_paid'])/df_portfolio_overview['total_price_paid']) * 100
    
    return df_portfolio_overview[['symbol', 'total_qt', 'total_price_paid', 'dca','current_market_value', 'profit_loss', 'percentage_change']]


def summary_get_deposits_usd_(kraken_deposit_history,kraken_account_size,binance_deposit_history,binance_account_size):
    # This function could be refactored and made shorter
    
    #get all kraken deposits
    kraken_deposit_h = np.float64(kraken_deposit_history['usd_base_price'].sum())
    #get kraken account current value
    kraken_account_s = np.float64(kraken_account_size.set_index('index').loc['balance_inUSDT'])
    # get percentage change 
    kraken_percentage_change = (kraken_account_s-kraken_deposit_h)/ kraken_deposit_h * 100

    #get all binance deposits
    binance_deposit_h = binance_deposit_history['usd_base_price'].sum()
    #get binance account current value
    binance_account_s = np.float64(binance_account_size.set_index('index').loc['balance_inUSDT'])
    #get percentage change
    binance_percentage_change = (binance_account_s-binance_deposit_h)/ binance_deposit_h * 100

    kraken_series = pd.Series([kraken_deposit_h,kraken_account_s,kraken_percentage_change],name='Kraken')
    binance_series = pd.Series([binance_deposit_h,binance_account_s,binance_percentage_change],name='Binance')
    deposits = pd.DataFrame([kraken_series,binance_series]).rename(columns={0:'Amount_deposited',1:'Current_value',2:'Percentage_Change'})
    return deposits

def summary_get_open_orders(dfs = list):
    
    summary_open_orders  = pd.DataFrame()
    
    for open_orders_exchange in dfs:
        summary_open_orders = pd.concat([summary_open_orders,open_orders_exchange])
    
    return summary_open_orders[['open_time','order','exchange']].reset_index(drop=True)

def summary_get_spot_balance(kraken_spot_balance,binance_spot_balance):
    df_portfolio_spot_balance = (
        pd.DataFrame([
        kraken_spot_balance.rename(columns={0:'kraken'}).squeeze()
        ,binance_spot_balance.set_index('index').rename(columns={0:'binance'}).squeeze()]
    ).T)
    
    return df_portfolio_spot_balance

def summary_get_savings_balance(binance_savings_overview,kraken_savings_overview):
    
    df_portfolio_spot_balance = (
        pd.concat([
            (pd.DataFrame(binance_savings_overview[0],index=['binance']).T)
            ,kraken_savings_overview.rename(columns={0:'kraken'})]
            ,axis=1))
    
    return df_portfolio_spot_balance

def summary_get_account_size(binance_account_size,kraken_account_size):
    
    df_portfolio_account_size = (
        pd.DataFrame([
        kraken_account_size.set_index('index').rename(columns={0:'kraken'}).squeeze()
        ,binance_account_size.set_index('index').rename(columns={0:'binance'}).squeeze()]
    ).T)
    
    df_portfolio_account_size.index.name = None
    return df_portfolio_account_size


def _sell_points_recomendations(symbol,total_price_paid, total_qt):
    
    sensibility = 0.0001 #price sensibility
    
    #get average price paid per coin
    cost_per_coin = total_price_paid / total_qt
    
    # get current trading price for our coin
    current_price = np.float64(Binanceclient.avg_price('{}USDT'.format(symbol))['price'])
    
    # check if price paid for is lower than current trading price. If not, no sell recommendation
    recomendations = collections.defaultdict(dict)
    if cost_per_coin < current_price and total_qt>0:
        sell_price_combinations = []
        for potential_sell_quantity in np.arange(0, total_qt,sensibility):
            sell_price_combinations.append({'sell_quantity':potential_sell_quantity,'trade_total':potential_sell_quantity * current_price})

        sell_price_combinations = pd.DataFrame(sell_price_combinations)
        recomendations['total_price_paid'] = total_price_paid
        recomendations['total_asset_available'] = total_qt
        recomendations['asset_current_trading_price'] = current_price
        recomendations['initial_investment_cover']= _sell_at_premium(sell_price_combinations,total_price_paid)
        recomendations['20_premium'] = _sell_at_premium(sell_price_combinations,total_price_paid,premium=1.2)
        recomendations['30_premium'] = _sell_at_premium(sell_price_combinations,total_price_paid,premium=1.3)
        recomendations['40_premium'] = _sell_at_premium(sell_price_combinations,total_price_paid,premium=1.4)
        recomendations['50_premium'] = _sell_at_premium(sell_price_combinations,total_price_paid,premium=1.5)
        
        return pd.DataFrame(recomendations,index=[symbol])
    
    return pd.DataFrame([{'total_price_paid':total_price_paid, 'total_asset_available':total_qt,'asset_current_trading_price':current_price, 'initial_investment_cover': 'Don\'t trade. Price needs to be higher', '20_premium': np.nan,'30_premium': np.nan, '40_premium':np.nan, '50_premium':np.nan}],index=[symbol])

def _sell_at_premium(df,total_price_paid,premium=1):
    df = df[df.trade_total.between(total_price_paid/1.01*premium,total_price_paid*1.01*premium)]
    if df.shape[0]==0:
        return ('Don\'t trade. Price needs to be higher.')
    return np.float64(df[df.index==df.trade_total.idxmax()]['sell_quantity'])



def summary_get_selling_recomendations_overview(df_portfolio_overview):
    
    df = df_portfolio_overview[['symbol', 'total_qt', 'total_price_paid', 'dca']].copy()
    recommendations = []
    for idx in range(df.shape[0]):
        symbol,total_price_paid, total_qt = df.iloc[idx]['symbol'],df.iloc[idx]['total_price_paid'],df.iloc[idx]['total_qt']
        recommendations.append(_sell_points_recomendations(symbol,total_price_paid, total_qt))
    
    return pd.concat(recommendations)  
