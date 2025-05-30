import os, pandas

def is_consolidating(df, percentage):
    if len(df) < 15: 
        return False

    recent_candlesticks = df[-15:]  # Sql equivalent ORDER BY date DESC LIMIT 15
    
    max_close = recent_candlesticks['Close'].max()
    min_close = recent_candlesticks['Close'].min()

    threshold = 1 - (percentage / 100)
    if min_close > (max_close * threshold):
        return True        

    return False

def is_breaking_out(df, percentage=2.5):
    if len(df) < 16:  # Ensure at least 16 rows exist
        return False

    last_close = df[-1:]['Close'].values[0]

    if is_consolidating(df[:-1], percentage=percentage):  #return True
        recent_closes = df[-16:-1]                        #ORDER BY date DESC LIMIT 15 OFFSET 1
        
        if last_close > recent_closes['Close'].max():
            return True

    return False

for filename in os.listdir('datasets/crypto_usdt_daily_data'):
    df = pandas.read_csv('datasets/crypto_usdt_daily_data/{}'.format(filename))
    #df = pandas.read_csv('datasets/crypto_usdt_daily_data/ADAUSDT.csv')
    if is_consolidating(df, percentage=2.5):
        print("{} is consolidating".format(filename))

    if is_breaking_out(df): #no need of percentage here
        print("{} is breaking out".format(filename))