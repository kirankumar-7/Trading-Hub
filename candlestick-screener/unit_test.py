'''
import talib
from binance.client import Client

client = Client()

interval = Client.KLINE_INTERVAL_1DAY
start_date = "2020-01-01"  # Start date for fetching data
end_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')  # End date as yesterday
symbol='SOLUSDT'

data = client.get_historical_klines(symbol, interval, start_date, end_date)

morning_star = talib.CDLMORNINGSTAR(data['Open'], data['High'], data['Low'], data['Close'])

engulfing = talib.CDLENGULFING(data['Open'], data['High'], data['Low'], data['Close']) 

data['Morning Star'] = morning_star  #columns added to dataframe
data['Engulfing'] = engulfing

engulfing_days = data[data['Engulfing'] != 0]

print(f'Engulfing Days:{engulfing_days}')

'''
import requests
from bs4 import BeautifulSoup

url = 'https://finviz.com/crypto_charts.ashx?t=SOLUSDT&c=USDT'
response = requests.get(url)

soup = BeautifulSoup(response.content, 'html.parser')
img_tag = soup.find('img')  # Find the image tag
img_url = img_tag['src']  # Extract the image URL

print(f"Direct image URL: {img_url}")
