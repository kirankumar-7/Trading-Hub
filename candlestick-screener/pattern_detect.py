########################## yfinance library ##################
'''
import talib
import yfinance as yf

data = yf.download("AAPL", start="2023-07-01", end="2024-07-08") #returns dataframe

morning_star = talib.CDLMORNINGSTAR(data['Open'], data['High'], data['Low'], data['Close'])

engulfing = talib.CDLENGULFING(data['Open'], data['High'], data['Low'], data['Close']) 

data['Morning Star'] = morning_star  #columns added to dataframe
data['Engulfing'] = engulfing

engulfing_days = data[data['Engulfing'] != 0]

print(f'Engulfing Days:{engulfing_days}')
'''

########################## binance library ##################
from binance.client import Client
import talib
import pandas as pd

client=Client()

start_str = '19 Feb, 2025'
end_str = '20 Feb, 2025'
interval = '1d'
symbol='SOLUSDT'

data = client.get_historical_klines(symbol, interval, start_str, end_str) #list of list

data = pd.DataFrame(data, columns=[
    'Timestamp', 'Open', 'High', 'Low', 'Close', 'Volume', 
    'CloseTime', 'QuoteAssetVolume', 'NumberOfTrades', 
    'TakerBuyBaseVolume', 'TakerBuyQuoteVolume', 'Ignore'
])


data[['Open', 'High', 'Low', 'Close']] = data[['Open', 'High', 'Low', 'Close']].astype(float)

morning_star = talib.CDLMORNINGSTAR(data['Open'], data['High'], data['Low'], data['Close'])
engulfing = talib.CDLENGULFING(data['Open'], data['High'], data['Low'], data['Close']) 

data['Morning Star'] = morning_star  #columns added to dataframe
data['Engulfing'] = engulfing

#print(data['Morning Star'])
#print(data['Engulfing'])
print(data)

'''
print(data)
       Timestamp    Open    High     Low   Close            Volume      CloseTime    QuoteAssetVolume  NumberOfTrades TakerBuyBaseVolume TakerBuyQuoteVolume Ignore  Morning Star  Engulfing
0  1739923200000  169.32  174.30  163.75  168.93  3478319.26200000  1740009599999  590112452.81958000         2185100   1718948.19000000  291753364.79675000      0             0          0
1  1740009600000  168.94  176.65  167.66  176.00  2938753.33500000  1740095999999  508528834.82322000         1920797   1457878.22300000  252304279.27536000      0             0          0
'''
