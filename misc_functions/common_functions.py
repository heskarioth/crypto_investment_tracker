

from sqlalchemy import create_engine
import sqlalchemy
import pandas as pd
import numpy as np
from global_vars import PAIRS
from portfolio_keys import *
from binance.spot import Spot 

from crypto_utils import _paring_returner,_price_coverter
Binanceclient = Spot(key=BINANCE_API_KEY, secret=BINANCE_PRIVATE_KEY)

def generic_dca_profit_loss(object,df_trades,exchange):
    
    df_trades['usd_base_price'] = df_trades.apply(lambda x: _price_coverter(x['pair'],x['operation_cost']),axis=1)
    
    #Step 2. Aggregate all trades per trading pair
    df_dca_symbol = df_trades.groupby(['pair','type'])[['crypto_vol','usd_base_price']].sum().reset_index()
    
    df_summary = pd.DataFrame()
    
    for symbol in PAIRS[exchange].keys():

        tmp = df_dca_symbol[df_dca_symbol.pair.isin(_paring_returner(symbol,exchange=exchange))].copy()
        # The above function might return No results sometimes because not necessarely we have tradeded the same 
        # asset across multiple exchanges
        if tmp.shape[0]>0:
            qt = []
            price = []
            for idx in range(tmp.shape[0]):
                #if transaction was BUY, we are increasing our asset balance (+) and decreasing our cash (-)
                if tmp.iloc[idx]['type'].upper()=='BUY':
                    qt.append(0 + tmp.iloc[idx]['crypto_vol'])
                    price.append(0 - tmp.iloc[idx]['usd_base_price'])
                # if we SELL, we are decreasing our asset balance (-) and increasing cash balance(+)
                else:
                    qt.append(0 - tmp.iloc[idx]['crypto_vol'])
                    price.append(0 + tmp.iloc[idx]['usd_base_price'])

            # get me current trading price for asset USDT denominated pair to calculate profit_Loss / current market value
            symbol_trading_price = np.float64(Binanceclient.avg_price('{}USDT'.format(symbol))['price'])

            df_summary = pd.concat(
                    [df_summary,pd.DataFrame(
                        {
                            'symbol':str(symbol)#'symbol':str(set(tmp.symbol))
                            ,'total_qt':np.float64(sum(qt))
                            ,'total_price_paid':np.float64(np.abs(sum(price)))
                            # dca = total amount spent / total quantity of asset
                            ,'dca': np.float64(np.abs(sum(price))/sum(qt) )
                            ,'current_market_value':np.float64((symbol_trading_price*sum(qt)))
                            ,'percentage_change': np.float64((np.float64((symbol_trading_price*sum(qt))) - np.float64(np.abs(sum(price)))) /np.float64(np.abs(sum(price)))) * 100
                            # profit_loss = how much would cost to buy our quantity now - how much we actually paid
                            ,'profit_loss':np.float64((symbol_trading_price*sum(qt)) - np.abs(sum(price)))
                            ,'current_trading_price': np.float64(symbol_trading_price)
                        },index=[0]
                     )]
                                 )

    return df_summary

def database_recon_update(df,tb_name,unique_identifier):
    """
        df - dataframe with latest data
        tb_name - table name that we need to update
        unique_identifier - record unique identifier to make sure we are not dealing with duplicate rows.
    """
    engine = create_engine('sqlite:///db/crypto_portfolio_.db',echo=False)
    
    
    sqlite_connection = engine.connect()
    
    try:
        
        # try to load existing dataset
        df_historical = pd.read_sql('SELECT * FROM {}'.format(tb_name),con=sqlite_connection)
        
        # compare with latest dataset, merge missing records and remove duplicates
        df_recon = pd.concat([df_historical,df]).drop_duplicates(subset=unique_identifier).copy()
        
        #delete old data and upload new one
        df_recon.to_sql(tb_name,sqlite_connection,index=False,if_exists='replace')
        sqlite_connection.close()
    
    except sqlalchemy.exc.OperationalError as err:
        
        # if table didn't exists, it's the first time we are uploading so just insert extraction as new table.
        if 'no such table' in (err.orig.args[0]):
            df.to_sql(tb_name,sqlite_connection,index=False,if_exists='replace')
            sqlite_connection.close()
            return df.reset_index(drop=True)
    
    return df_recon.reset_index(drop=True)
        
