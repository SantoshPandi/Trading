import pandas as pd
import schedule
import time
import numpy as np
  
import krakenex
from pykrakenapi import KrakenAPI
api = krakenex.API()
k = KrakenAPI(api)
api.load_key("KrakenKeys.py")
def main():
    print('Starting Script...')
    schedule.every(1).minutes.do(entry_exit_logic)
    while True:
        schedule.run_pending()
        time.sleep(1)

def entry_exit_logic():
    print('Logic Check')
    # Calculate metrics
    currency = 'ZUSD'
    crypto = 'XETH'
    pair = crypto + currency
    df = k.get_ohlc_data(pair)[0].sort_index()
    ewm_3 = df['close'].ewm(3).mean()[-1]
    
#Get Bought Price + Fee Paid
    #Get Last Sold Price
    df_lastsold = k.get_trades_history()[0].sort_index()    
    df_ledger_lastsold = pd.DataFrame(df_lastsold)
    df_ledger_lastsold1 = df_ledger_lastsold.loc[df_ledger_lastsold['pair']=='XETHZUSD']
    df_ledger_lastsold1 = df_ledger_lastsold1.loc[df_ledger_lastsold['type']=='sell']
    df_ledger_lastsold2 = df_ledger_lastsold1['price']
    svalue = pd.DataFrame(df_ledger_lastsold2)
    svalue = svalue.tail(1)
    lastsoldprice_latest = svalue.iloc[0]['price']
    print("LastSoldPrice : ",lastsoldprice_latest)
    df_ledger_fee_last_sold = df_ledger_lastsold1['fee']
    lastsold_fvalue = pd.DataFrame(df_ledger_fee_last_sold)
    lastsold_fvalue = lastsold_fvalue.tail(1)
    fee_latest_sold = lastsold_fvalue.iloc[0]['fee']
    print("FeePaid : ",fee_latest_sold) 
    df_ledger_fee_last_vol = df_ledger_lastsold1['vol']
    lastsold_vol = pd.DataFrame(df_ledger_fee_last_vol)
    lastsold_vol = lastsold_vol.tail(1)
    vol_latest_sold = lastsold_vol.iloc[0]['vol']
    print("Volume : ",vol_latest_sold) 
    LastSoldPrice = lastsoldprice_latest + fee_latest_sold
    print("Fee+SoldPrice",LastSoldPrice)
    
    #Get Last Bought Price 
    df_last_buy = k.get_trades_history()[0].sort_index()     
    df_ledger_last_buy = pd.DataFrame(df_last_buy)
    df_ledger_last_buy1 = df_ledger_last_buy.loc[df_ledger_last_buy['pair']=='XETHZUSD']
    df_ledger_last_buy1 = df_ledger_last_buy1.loc[df_ledger_last_buy['type']=='buy']
    df_ledger_lastbuy2 = df_ledger_last_buy1['price']
    bvalue = pd.DataFrame(df_ledger_lastbuy2)
    bvalue = bvalue.tail(1)
    lastbuyprice_latest = bvalue.iloc[0]['price']
    print(lastbuyprice_latest)
    df_ledger_fee_last_buy = df_ledger_last_buy1['fee']
    lastbuy_bvalue = pd.DataFrame(df_ledger_fee_last_buy)
    lastbuy_bvalue = lastbuy_bvalue.tail(1)
    fee_latest_buy = lastbuy_bvalue.iloc[0]['fee']
    print("FeePaid : ",fee_latest_buy) 
    LastBuyPrice = abs(lastbuyprice_latest) + fee_latest_buy
    print("Fee+BoughtPrice",LastBuyPrice)
    
    
    df = k.get_ohlc_data(pair)[0].sort_index()
    ewm_last= df['close']
    lastvalue = pd.DataFrame(ewm_last)
    lastvalue = lastvalue.tail(1)
    cp = lastvalue.iloc[0]['close']
    print("CurrentPrice",cp)
    lowerlimit = (LastBuyPrice) - ((((LastBuyPrice)*3)/100))
    higherlimit = (LastBuyPrice) + ((((LastBuyPrice)*2)/100))

    print("LowLimitToSell",lowerlimit)  
    print("HighLimitToSell",higherlimit)
    
    #ewm_30 = df['close'].ewm(30).mean()[-1]    
    #ewm_60 = df['close'].ewm(60).mean()[-1]    
    #ewm_120 = df['close'].ewm(120).mean()[-1]
    
    # Current holdings
    volume = k.get_account_balance()
    try:
        cash_on_hand = volume.loc[currency][0]
    except:
        print('No USD On Hand.')
        pass
    try:
        crypto_on_hand = volume.loc[crypto][0]       
    except:
        print('No Cryptocurreny On Hand.')
        pass
    
    try:       
        holding_crypto = [True if volume.loc[crypto][0] >= 1 else False][0]      
        #print(holding_crypto)
        
    except:
        print('No Cryptocurreny On Hand.')
        pass
    
    try:   
        current_price = df['close'][-1]       
    except:
        print('No Cryptocurreny On Hand.')
        pass
    
    try:           
        affordable_shares = int(cash_on_hand/current_price)
    except:
        print('No Cryptocurreny On Hand.')
        pass
    

    # Entry-Exit Logic
    if (cp < LastBuyPrice) & (holding_crypto==False):
        type = 'buy'
        api.query_private('AddOrder', {'pair': pair, 'type': type, 'ordertype':'market', 'volume': affordable_shares})
        print('------------------------------------>Bought Shares')
   
    elif (cp > higherlimit) & (holding_crypto==True):
        type = 'sell'
        api.query_private('AddOrder', {'pair': pair, 'type': type, 'ordertype':'market', 'volume': crypto_on_hand})
        print('------------------------------------>Sold Shares')
        
    #elif (cp <= lowerlimit)  & (holding_crypto==True):
     #   type = 'sell'
      #  api.query_private('AddOrder', {'pair': pair, 'type': type, 'ordertype':'market', 'volume': crypto_on_hand})
       # print('------------------------------------>Sold Shares')
            
    else :
        print('------------------------------------>Holding')
        pass

if __name__ == '__main__':
    main()
