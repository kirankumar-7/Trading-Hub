from binance.client import Client
import pandas as pd
from datetime import datetime

client = Client()

start_str = '1 Jan, 2024'
end_str = '16 Nov, 2024'
interval = '1d'

def snapshot():
    with open('datasets/crypto_usdt_symbols.csv', 'r') as f:
        for symbol in f:
            symbol = symbol.strip()
            try:
                data = client.get_historical_klines(symbol, interval, start_str, end_str)

                processed_data = []
                for x in data:
                    row = [
                        datetime.fromtimestamp(x[0] / 1000).strftime('%Y-%m-%d'),  #timestamp to Date
                        float(x[1]),  # Open
                        float(x[2]),  # High
                        float(x[3]),  # Low
                        float(x[4]),  # Close
                        float(x[5]),  # Volume
                        int(x[8])     # Number of trades
                    ]
                    processed_data.append(row)

                df = pd.DataFrame(processed_data, columns=[
                        'Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'Number of trades'
                        ])
                
                df.to_csv(f'datasets/crypto_usdt_daily_data/{symbol}.csv', index=False)
                print('{} Data loaded to csv file successfully'.format(symbol))
            except Exception as e:
                print(f"Failed to fetch data for {symbol}: {e}")
    
    print('Data Extrated from binance API for the given symbols successfully')

snapshot()
