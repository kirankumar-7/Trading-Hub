import os, csv
import json
import talib
import pandas as pd
from flask import Flask, request, render_template
from strategies.indicators import pivot_levels
from binance.client import Client
import psycopg2

# Build path to config file
config_path = os.path.join('config', 'dbconfig.json')

# Load JSON config
with open(config_path) as f:
    DB_CONFIG = json.load(f)

app = Flask(__name__)

client = Client()

start_str = '1 Jan, 2024'
end_str = '16 Nov, 2024'
interval = '1d'

@app.route('/')
def home():
    return f'''
        <h1>Welcome to Crypto Candle Stick Screener</h1>
        <p>Select an option below:</p>
        <ul>
            <li><a href="/snapshot">Snapshot</a> - Download all historical Binance Crypto data in a CSV file.</li>
            <li><a href="/patternDetect">Pattern Detection</a> - Run the candlestick pattern screener.</li>
        </ul>
    '''

@app.route('/snapshot')
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
    
    return 'Data Extrated from binance API for the given symbols successfully'

@app.route('/patternDetect')
def index():
    pattern = request.args.get('pattern', '')
    crypto = {}

    try:
        # Connect to PostgreSQL
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        query = """
                SELECT open, high, low, close, symbol 
                FROM crypto_last_trade_date_dtls
                """
        cursor.execute(query)
        rows = cursor.fetchall()

        if rows:
            # Convert to DataFrame
            df = pd.DataFrame(rows, columns=['Open', 'High', 'Low', 'Close', 'Symbol'])

            # Group by symbol and apply the pattern detection
            for symbol, group in df.groupby('Symbol'):
                try:
                    # Apply TA-Lib function
                    pattern_function = getattr(talib, pattern)
                    results = pattern_function(group['Open'], group['High'], group['Low'], group['Close'])
                    last = results.iloc[-1]  # Get the latest pattern signal
                    print(f'Last signal for {symbol}:', last)

                    # Initialize symbol dictionary
                    if symbol not in crypto:
                        crypto[symbol] = {}

                    if last > 0:
                        crypto[symbol][pattern] = 'bullish'
                    elif last < 0:
                        crypto[symbol][pattern] = 'bearish'
                    else:
                        crypto[symbol][pattern] = None

                except Exception as e:
                    print(f'Pattern detection failed for {symbol}: {e}')

        cursor.close()
        conn.close()

    except Exception as e:
        print(f"Database error: {e}")

    print(crypto)
    return render_template('index.html', candlestick_patterns=candlestick_patterns, crypto=crypto, pattern=pattern)
    
@app.route('/predict', methods=['POST'])  # For testing via Postman
def predict():
    if request.method == 'POST':
        high = float(request.json['high'])
        low = float(request.json['low'])
        close = float(request.json['close'])

        result_json = pivot_levels(high, low, close)
        return jsonify(json.loads(result_json))

if __name__ == '__main__':
    app.run(debug=True)