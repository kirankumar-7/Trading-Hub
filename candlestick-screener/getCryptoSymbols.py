#to get crypto symbols and save in a csv file

from binance.client import Client
import csv
import psycopg2

client = Client()

def get_crypto_symbols():
    try:
        exchange_info = client.get_exchange_info()
        symbols = [item['symbol'] for item in exchange_info['symbols']]
        return symbols

    except Exception as e:
        raise RuntimeError(f"Could not fetch crypto symbols: {e}")


def post_symbols_to_csv(symbols, filename='C:/Users/Kiran/Desktop/binanceCryptoData/candlestick-screener/datasets/crypto_all_symbols.csv'):
    try:
        with open(filename, mode='w', newline='') as file:
            writer = csv.writer(file)
            
            for symbol in symbols:
                writer.writerow([symbol])
                
        print(f"Symbols saved successfully to {filename}")
    except Exception as e:
        raise RuntimeError(f"Could not save symbols to CSV: {e}")

symbols = get_crypto_symbols()
#post_symbols_to_csv(symbols)

'''
#######   create below table in database  ###########

CREATE TABLE crypto_symbols_usdt (
    symbols_usdt VARCHAR(50) NOT NULL,    
    added_by VARCHAR(50) NOT NULL default 'binanceapi',        
    added_date TIMESTAMP DEFAULT now()
);
'''
def post_symbols_to_database(symbols):
    try:
        conn = psycopg2.connect("host=localhost dbname=cryptodb user=postgres password=postgres")
        cur = conn.cursor()
        conn.set_session(autocommit=True)
        
        # Loop through symbols and insert into the database
        for symbol in symbols:
            try:
                cur.execute("""
                    INSERT INTO crypto_symbols_usdt (symbols_usdt) 
                    VALUES (%s)
                """, (symbol,))
                print(f"Data for {symbol} inserted successfully in crypto_symbols_usdt table.")
            except Exception as e:
                print(f"Error inserting the data for {symbol}: {e}")
        
    except psycopg2.Error as e:
        print(f"Error: Could not make connection to the Postgres database: {e}")
        exit()
    
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()
        print("Database connection closed.")
        
post_symbols_to_database(symbols)

'''
#####Transformation#####

create table crypto_all_symbols as
select * from crypto_symbols_usdt

SELECT * FROM crypto_symbols_usdt
WHERE RIGHT(symbols_usdt, 4) = 'USDT';

ALTER TABLE crypto_symbols_usdt RENAME TO crypto_usdt_symbols;
'''