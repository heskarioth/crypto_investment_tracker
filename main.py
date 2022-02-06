import time
from binance.spot import Spot
from api.krakenapi import KrakenAPI
from portfolio_keys import * 
from api.exchange_functions.binance_funcs import *
from api.exchange_functions.kraken_funcs import *
from sheets_utils.backend_sheet_funcs import *
from misc_functions.summary_funcs import * 
from misc_functions.watchlist_funcs import *

def main():
    
    
    ######################################### Binance #########################################
    
     #update overview tab
    Binanceclient = Spot(key=BINANCE_API_KEY, secret=BINANCE_PRIVATE_KEY)
    global binance_dca_df
    binance_dca_df = binance_dca_profit_loss(Binanceclient)
    updater(df=binance_dca_df[['symbol', 'total_qt', 'total_price_paid', 'dca', 'current_market_value','percentage_change', 'profit_loss']],sheetname='Binance',start_cell='A2',clean=False)
    
    global binance_trades_history
    #update history trades 
    binance_trades_history = binance_get_all_trades(Binanceclient)
    updater(df=binance_trades_history.sort_values(by='time_epoch',ascending=True),sheetname='Binance_Trade_H',start_cell='A1',clean=True)
    update_dropdown_binance(binance_trades_history,start_cell='A2')
    
    
    #get open orders
    global binance_open_orders 
    binance_open_orders  = binance_get_open_orders(Binanceclient)
    updater(df=binance_open_orders,sheetname='Binance',start_cell='A19',row_names=False,col_names=True,clean=False)
    
    #get interest history
    global binance_interest_history
    binance_interest_history = binance_get_past_dividends(Binanceclient)


    updater(df=binance_interest_history.sort_values(by='divTime_epoch',ascending=True),sheetname='Binance_Interest_H',start_cell='A1',clean=True)
    
    # get savings balance
    global binance_savings_overview
    binance_savings_overview = binance_get_savings(Binanceclient,binance_interest_history)
    updater(df=pd.DataFrame(binance_savings_overview[0],index=[0]).T,sheetname='Binance',start_cell='I2',clean=False,col_names=False,row_names=True)
    
    updater(df=binance_savings_overview[1],sheetname='Binance',start_cell='L2',clean=False,col_names=True,row_names=False)

    #get spot balance
    global binance_spot_balance
    binance_spot_balance = binance_get_spot_balance(Binanceclient)
    updater(df=binance_spot_balance,sheetname='Binance',start_cell='I7',row_names=False,col_names=False,clean=False)
    
    #get total account balance
    global binance_account_size
    binance_account_size = binance_get_total_account_size(Binanceclient)
    updater(df=binance_account_size,sheetname='Binance',start_cell='I11',row_names=False,col_names=False,clean=False)
    
    #get deposit history
    global binance_deposit_history
    binance_deposit_history = binance_get_deposit_history(Binanceclient)
    updater(df=binance_deposit_history.reset_index(drop=True),sheetname='Binance_Deposit_H',start_cell='A1',row_names=False,col_names=True,clean=True)
    
    time.sleep(61)
    ######################################## Kraken #########################################
    
    # get overview tab
    global kraken_dca_df
    Krakenclient = KrakenAPI()
    kraken_dca_df = kraken_dca_profit_loss(Krakenclient)
    updater(df=kraken_dca_df[['symbol', 'total_qt', 'total_price_paid', 'dca', 'current_market_value','percentage_change', 'profit_loss']],sheetname='Kraken',start_cell='A2',clean=False)
    
    global kraken_df_savings
    global kraken_savings_overview
    #get savings 
    kraken_savings_overview,kraken_df_savings= kraken_get_savings(Krakenclient)
    #update savings overview
    updater(df=kraken_savings_overview,sheetname='Kraken',start_cell='I2',row_names=True,col_names=False,clean=False)
    #update savings details
    updater(df=kraken_df_savings,sheetname='Kraken',start_cell='L2',row_names=False,col_names=True,clean=False)

    #get spot balance
    global kraken_spot_balance
    kraken_spot_balance = kraken_get_spot_balance(Krakenclient)
    updater(df=kraken_spot_balance,sheetname='Kraken',start_cell='I7',row_names=True,col_names=False,clean=False)
    
    #get open orders
    global kraken_open_orders
    kraken_open_orders = kraken_get_open_orders(Krakenclient)[['pair', 'vol', 'price', 'type', 'open_time', 'order','exchange']]
    updater(df=kraken_open_orders,sheetname='Kraken',start_cell='A19',row_names=False,col_names=True,clean=False)
    
    #upate trades history
    global kraken_transaction_history
    kraken_transaction_history = kraken_get_transactions_history(Krakenclient)
    updater(df=kraken_transaction_history,sheetname='Kraken_Trade_H',start_cell='A1',row_names=False,col_names=True,clean=True)
    
    #update interest history
    global kraken_interest_history
    kraken_interest_history = kraken_get_interest_history(Krakenclient)
    updater(df=kraken_interest_history,sheetname='Kraken_Interest_H',start_cell='A1',row_names=False,col_names=True,clean=True)
    
    #update account size
    global kraken_account_size
    kraken_account_size = kraken_get_total_account_size(Krakenclient)
    updater(df=kraken_account_size,sheetname='Kraken',start_cell='I11',row_names=False,col_names=False,clean=False)
    
    # get deposit history
    global kraken_deposit_history
    kraken_deposit_history = kraken_get_deposit_history(Krakenclient)
    updater(df=kraken_deposit_history.reset_index(drop=True),sheetname='Kraken_Deposit_H',start_cell='A1',row_names=False,col_names=True,clean=True)
    
    #add dropdown menu
    update_dropdown_kraken(kraken_transaction_history,start_cell='B2')
  
    time.sleep(61)
    ################################################## Summary Tab ###################################################
    
    # add dca overview
    global df_portfolio_overview
    df_portfolio_overview = summary_get_overview_tab(kraken_dca_df,binance_dca_df)
    updater(df=df_portfolio_overview,sheetname='Summary',start_cell='A2',row_names=False,col_names=True,clean=False)
    
    # add open orders 
    global df_portfolio_open_orders
    df_portfolio_open_orders = summary_get_open_orders([kraken_open_orders,binance_open_orders])
    updater(df=df_portfolio_open_orders,sheetname='Summary',start_cell='E20',row_names=False,col_names=True,clean=False) 
    
    # add deposits
    global df_portfolio_deposits
    df_portfolio_deposits = summary_get_deposits_usd_(kraken_deposit_history,kraken_account_size,binance_deposit_history,binance_account_size)
    updater(df=df_portfolio_deposits,sheetname='Summary',start_cell='J17',row_names=True,col_names=True,clean=False)
    
    # add spot balance
    global df_portfolio_spot_balance
    df_portfolio_spot_balance = summary_get_spot_balance(kraken_spot_balance,binance_spot_balance)
    updater(df=df_portfolio_spot_balance,sheetname='Summary',start_cell='J7',row_names=True,col_names=True,clean=False)
    
    #add savings balance
    global df_portfolio_savings_balance
    df_portfolio_savings_balance = summary_get_savings_balance(binance_savings_overview,kraken_savings_overview)
    updater(df=df_portfolio_savings_balance,sheetname='Summary',start_cell='J2',row_names=True,col_names=True,clean=False)
    
    #add account balance
    global df_portfolio_account_size
    df_portfolio_account_size = summary_get_account_size(binance_account_size,kraken_account_size)
    updater(df=df_portfolio_account_size,sheetname='Summary',start_cell='J12',row_names=True,col_names=True,clean=False)

    #add account recommendation 
    global df_portfolio_selling_recommendation
    df_portfolio_selling_recommendation = summary_get_selling_recomendations_overview(df_portfolio_overview)
    updater(df=df_portfolio_selling_recommendation,sheetname='Summary',start_cell='Q2',row_names=True,col_names=True,clean=False)

    ##################################################### WatchList Tab #####################################
    global watchlist_overview
    watchlist_overview = watchlist_get_overview()
    updater(df=watchlist_overview,sheetname='WatchList',start_cell='A2',row_names=False,col_names=True,clean=False)




if __name__=='__main__':
    main()