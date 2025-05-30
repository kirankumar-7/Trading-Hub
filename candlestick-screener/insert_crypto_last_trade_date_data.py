from binance.client import Client
from datetime import datetime, timedelta
import psycopg2

# Initialize Binance client
client = Client()

# Connect to the PostgreSQL database
try: 
    conn = psycopg2.connect("host=localhost dbname=cryptodb user=postgres password=postgres")
    cur = conn.cursor()
    conn.set_session(autocommit=True)
except psycopg2.Error as e:
    print(f"Error: Could not make connection to the Postgres database: {e}")
    exit()

try:
    cur.execute("SELECT symbols_usdt FROM crypto_usdt_symbols")
    usdt_pairs = [row[0] for row in cur.fetchall()]  # Extract symbols into a list
    
    if not usdt_pairs:
        print("No USDT pairs found in the database.")
        exit()
except Exception as e:
    print(f"Error in getting usdt_pairs: {e}")
    
try:
    # Define the interval and date range
    interval = Client.KLINE_INTERVAL_1DAY
    start_date = (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d')  # Start of today
    end_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    
    # Single loop to process each symbol
    for symbol in usdt_pairs:   
        try:
            # Fetch historical kline data for the symbol
            historical_data = client.get_historical_klines(symbol, interval, start_date, end_date)
            print('symbol',historical_data)
            
            for kline in historical_data:
                trade_date = datetime.fromtimestamp(kline[0] / 1000)  # Open time
                open_price = float(kline[1])
                high_price = float(kline[2])
                low_price = float(kline[3])
                close_price = float(kline[4])
                adj_close_price = close_price  # Assuming adjusted close is same as close
                volume = float(kline[5])
                trade_count = kline[8]  # Number of trades

                # Determine the appropriate table based on the year
                table_name = f"crypto_last_trade_date_dtls"
                print(f"tablename is: {table_name}")

                # Insert data into the respective partition table
                cur.execute(
                    f"""
                    INSERT INTO {table_name} 
                    (trade_date, symbol, open, high, low, close, adj_close, volume, added_by_id, total_trade_count)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (trade_date, symbol, open_price, high_price, low_price, close_price, 
                     adj_close_price, volume, 'binanceapi', trade_count)
                )
                print(f"Data inserted successfully for {symbol} at {trade_date} in {table_name}.")

        except Exception as e:
            print(f"Error processing data for {symbol}: {e}")

except Exception as e:
    print(f"Error in processing: {e}")

finally:
    # Close cursor and connection
    if cur:
        cur.close()
    if conn:
        conn.close()
 
