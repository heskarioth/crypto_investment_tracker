## backendfunctions for sheets
import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials
from df2gspread import df2gspread as d2g

scope = ["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/spreadsheets',"https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("sheets_utils/sheets_creds.json", scope)
#creds = ServiceAccountCredentials.from_json_keyfile_name("sheets_creds.json", scope)

client = gspread.authorize(creds)
GOOGLE_SHEET_ID = '1GO914FoLUKr_UwP9FRXkNq-Al3GLtjdZM_fvd53FKNI'
crypto_p = client.open_by_key(GOOGLE_SHEET_ID)



def updater(df,sheetname,clean=True,col_names=True,row_names=False,start_cell='A1'):
    
    # Documentation: https://df2gspread.readthedocs.io/en/latest/examples.html
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

def update_dropdown_binance(df,start_cell):
    if start_cell==None:
        start_cell='A1'
    tmp = df.copy()
    pattern = '|'.join(['USDT', 'GBP','BUSD'])
    tmp['filter'] = tmp.symbol.str.replace(pattern,'', regex=True)
    series = pd.Series(tmp['filter'].value_counts().index)

    updater(df=pd.DataFrame(series),sheetname='List',clean=False,col_names=False,row_names=False,start_cell=start_cell)

def update_dropdown_kraken(df,start_cell):
    if start_cell==None:
        start_cell='A1'
    tmp = df.copy()
    pattern = '|'.join(['USDT', 'GBP','BUSD','EUR'])
    tmp['filter'] = tmp.pair.str.replace(pattern,'', regex=True)
    series = pd.Series(tmp['filter'].value_counts().index)
    updater(df=pd.DataFrame(series),sheetname='List',clean=False,col_names=False,row_names=False,start_cell=start_cell)
