# Crypto Investment Tracker

Tired of keeping track of your crypto portfolio across multiple exchanges? 
Crypto Investment Tracker enables you to keep track of all your crypto holdings across all your providers (currently support for Binance and Kraken.com is enabled). 


### Installation

#### Dashboard Set up
This project makes use of Google Sheets for the Dashboard front-end and Python for back-end jobs. In order to set up a correct connection between the two,
you need to create a ServiceAccount in Google Developer Console, enable Google Sheets API, share access to Google Sheet File to that ServiceAccount and create API Keys. You can follow [this guide](https://www.twilio.com/blog/2017/02/an-easy-way-to-read-and-write-to-a-google-spreadsheet-in-python.html) 
to get you up and running. After downloading the JSON credential file, rename it as <i>sheets_creds.json</i> and place it under the <i>sheets_utils</i> folder. The code is expecting a predefined template to be used as Dashboard, please make sure to copy [this template](https://docs.google.com/spreadsheets/d/1Cds4zfSrhxVSPzneG5EKlQXIj9lL2KfSlxH2d8kNWrc/edit?usp=sharing) 
and rename it <b>Crypto Investment Tracker</b>. Finally, ensure that your Sheet ID has been given to the <i>GOOGLE_SHEET_ID</i> variable in <i>global_vars</i>.

#### Installation
To install the package, go to location where you want to save project and follow the below commands:
```bash
git clone https://github.com/heskarioth/crypto_investment_tracker.git
cd crypto_investment_tracker
python3 setup.py install
```

#### API Exchange keys set up
This project utilises Kraken and Binance. Follow [this link](https://www.binance.com/en/support/faq/360002502072) for instructions on how to create API keys for Binance and [this](https://support.kraken.com/hc/en-us/articles/360000919966-How-to-generate-an-API-key-pair-) 
other one for Kraken. Their corresponding values should be given to the variables below in <i>portfolio_keys</i> module. Don't forget to also amend <i>INVESTED_COINS</i> with the list of coins you're holding.
```bash
KRAKEN_API_KEY = '????????????????????????????????????????????????'
KRAKEN_PRIVATE_KEY = '???????????????????????????????????????????????'

BINANCE_API_KEY = '??????????????????????????????????????'
BINANCE_PRIVATE_KEY = '??????????????????????????????????????'

INVESTED_COINS = ['BTC','ADA','AAVE','HBAR','STX','BNB','MATIC'] # This is the list of coins I have.
```

### Usage
From terminal, go to location repo was saved and execute below line:
```cmd
python3 main.py

```

### Dashboard Documentation

The Dashboard is structured in four parts (or tabs). 
- ***Summary** tab includes a broad overview of all your portfolio holding across the different exchanges, balances, savings, open orders, selling recommendations, and portfolio asset allocation breakdown, current value and profit_loss.*
- ***Binance** tab includes all holdings' information including: historical trades, acrrued interest, balances, open orders and profit-loss for the Binance Exchange.*
- ***Kraken** tab includes all holdings' information including: historical trades, acrrued interest, balances, open orders and profit-loss for the Kraken Exchange.*
- ***WatchList** tab includes all latest market data for crypto assets in our watchlist. The data here is taken from [CoinGecko](https://www.coingecko.com/en/api/documentation).*

Methods description:
- *Summary*
  - Get me an overview of all my crypto holdings. Include total token quantity, dca, profit_loss, price paid, and current asset value.
    ```python 
    summary_get_overview_tab(kraken_dca_df,binance_dca_df)
    ```
  - Get me all my open orders across all the exchanges.
    ```python 
    summary_get_open_orders([kraken_open_orders,binance_open_orders])
    ```  
  - Get me how much I have deposited in all my accounts.
    ```python
    summary_get_deposits_usd_(kraken_deposit_history,kraken_account_size,binance_deposit_history,binance_account_size)
    ```
  - Get me total available spot balance across all exchanges (in BTC and USDT)
    ```python
    summary_get_spot_balance(kraken_spot_balance,binance_spot_balance)
    ```
  - Get me total savings account balance across all exchanges (in BTC and USDT).
    ```python 
    summary_get_savings_balance(binance_savings_overview,kraken_savings_overview)
    ```
  - Get me total account size across all exchanges (in BTC and USDT).
    ```python 
    summary_get_account_size(binance_account_size,kraken_account_size)
    ```  
  - Give my trade history, suggest me selling prices for the crypto I own.
    ```python
    summary_get_selling_recomendations_overview(df_portfolio_overview)
    ```
- *Binance*
  - Get me an overview of all my crypto holdings in Binance. Include total token quantity, dca, profit_loss, price paid, and current asset value.
    ```python 
    binance_dca_profit_loss(Binanceclient)
    ```
  - Get me all trade history.
    ```python 
    binance_get_all_trades(Binanceclient)
    ```
  - Get me all pending orders in Binance.
    ```python 
    binance_get_open_orders(Binanceclient)
    ```
  - Get me all past dividend payments.
    ```python 
    binance_get_past_dividends(Binanceclient)
    ```
  - Get me Binance savings balance.
    ```python 
    binance_get_savings(Binanceclient,binance_interest_history)
    ```
  - Get me Binance spot balance.
    ```python 
    binance_get_spot_balance(Binanceclient)
    ```
  - Get me BInance account size.
    ```python 
    binance_get_total_account_size(Binanceclient)
    ```
  - Get me fiat deposit history to Binance.
    ```python
    binance_get_deposit_history(Binanceclient)
    ```
- *Kraken*
  - Get me an overview of all my crypto holdings in Kraken. Include total token quantity, dca, profit_loss, price paid, and current asset value.
    ```python
    kraken_dca_profit_loss(Krakenclient)
    ```
  - Get me total savings account balance (in BTC and USDT).
    ```python
    kraken_get_savings(Krakenclient)
    ```
  - Get me total spot account balance (in BTC and USDT).
    ```python
    kraken_get_spot_balance(Krakenclient)
    ```
  - Get me all pending orders in Kraken.
    ```python
    kraken_get_open_orders(Krakenclient)
    ```
  - Get me all trade history in Kraken.
    ```python
    kraken_get_transactions_history(Krakenclient)
    ```
  - Get me all past dividend payments.
    ```python
    kraken_get_interest_history(Krakenclient)
    ```
  - Get me Kraken account size.
    ```python
    kraken_get_total_account_size(Krakenclient)
    ```
  - Get me fiat deposit history to Kraken.
    ```python
    kraken_get_deposit_history(Krakenclient)
    ```  
- *WatchList*
  - Given my watchlist, return me a daily snapshot overview.
    ```python
    watchlist_get_overview()
    ```

### Dashboard Custimization and Extensions

All the market data extracted for our coins is saved into a sqllite db. This means we can use that data to do other calculations and extend our dashboards.
If you want to do so, make sure to use the [d2gspread library](https://df2gspread.readthedocs.io/en/latest/examples.html) to speed up data loading to the dashboard:
```python
def updater(df,sheetname,clean=True,col_names=True,row_names=False,start_cell='A1'): 
    d2g.upload(
        df
        ,gfile=GOOGLE_SHEET_ID
        ,wks_name=sheetname
        ,credentials=creds
        ,clean=clean
        ,col_names=col_names
        ,row_names=row_names
        ,start_cell=start_cell
            )
```
One important note to consider is that not all trading pairs will be available across all your exchange accounts. For instance, you can't trade AAVE as AAVEEUR on Binance because it is not available but you can trade it
on Kraken. For this reason we have to manually update the <i>PAIRS</i> in <i>global_vars</i> to reflect the difference, e.g.
```python
PAIRS = {
        'BINANCE': {'AAVE':['AAVEUSDT']}
        ,'KRAKEN': {'AAVE':['AAVEEUR']}
         }
```
Moreover, I am not sure abut you but I've received few shitcoins on Binance as airdrops and I have no intention of following them, here we can make sure to ignore them.
Similarly, if we want to change the scope of the watchlist cryptos, then we can amend <i>COIN_WATCHLIST_GECKO_SYMBOL</i>:
```python
COIN_WATCHLIST_GECKO_SYMBOL = ['btc','eth','usdt','bnb','usdc','sol','ada','dot','luna']
```

### Future Development
Below some of the development items for the next iteration:
- Integrate other exchages: blockchain.com, coinbase, crypto.com
- Introduce concurrency

To follow latest development effort on this project, please follow related [Trello board](https://trello.com/b/NA93gt0W/crypto-portfolio).
### License
[MIT](https://choosealicense.com/licenses/mit/)
