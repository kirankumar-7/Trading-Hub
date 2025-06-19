import os, csv
import json
import talib
import pandas as pd
from flask import Flask, request, render_template
from binance.client import Client
import psycopg2

# Build path to config file
config_path = os.path.join('config', 'dbconfig.json')

# Load JSON config
with open(config_path) as f:
    DB_CONFIG = json.load(f)

app = Flask(__name__)

client = Client()

@app.route('/')
def home():
    return f'''
        <h1>Welcome to Crypto Candle Stick Screener</h1>
        <p>Select an option below:</p>
        <ul>
            <li><a href="/patternDetect">Pattern Detection</a> - Run the candlestick pattern screener.</li>
        </ul>
    '''

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

if __name__ == '__main__':
    app.run(debug=True)