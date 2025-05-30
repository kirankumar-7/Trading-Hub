import talib
import pandas as pd
import psycopg2
from sqlalchemy import create_engine

# Database connection using SQLAlchemy for Pandas compatibility
db_url = "postgresql://postgres:postgres@localhost:5432/cryptodb"
engine = create_engine(db_url)
conn = psycopg2.connect(
    dbname="cryptodb",
    user="postgres",
    password="postgres",
    host="localhost",
    port="5432"
)
cursor = conn.cursor()

# Fetch candlestick pattern codes dynamically from the database
cursor.execute("SELECT pattern FROM crypto_candlestick_patterns")
candlestick_patterns = {row[0] for row in cursor.fetchall()}  # Set of patterns

# Fetch unique symbols
cursor.execute("SELECT symbols_usdt FROM crypto_usdt_symbols")
symbols = [row[0] for row in cursor.fetchall()]

# Process each symbol
for symbol in symbols:
    # Fetch historical candlestick data from the database
    query = f"""
    SELECT trade_date, open, high, low, close FROM crypto_candle_scanner_2025_data
    WHERE symbol = '{symbol}' ORDER BY trade_date;
    """
    
    # Use SQLAlchemy engine instead of psycopg2 connection
    df = pd.read_sql(query, engine)

    # Ensure numeric columns are floats
    df[['open', 'high', 'low', 'close']] = df[['open', 'high', 'low', 'close']].astype(float)

    # Apply TA-Lib candlestick pattern detection
    for pattern_code in candlestick_patterns:  # Iterate directly over the set
        df[pattern_code] = getattr(talib, pattern_code)(df['open'], df['high'], df['low'], df['close'])

    # Process detected patterns
    updates = []
    for index, row in df.iterrows():
        detected_patterns = []
        trend = "none"

        for pattern_code in candlestick_patterns:
            if row[pattern_code] > 0:
                detected_patterns.append(pattern_code)
                trend = "bullish"
            elif row[pattern_code] < 0:
                detected_patterns.append(pattern_code)
                trend = "bearish"

        detected_patterns_str = ', '.join(detected_patterns) if detected_patterns else None
        updates.append((trend, detected_patterns_str, row['trade_date'], symbol))

    # Update database with detected patterns
    update_query = """
    UPDATE crypto_candle_scanner_2025_data
    SET candle_pattern_trend = %s, candle_pattern_detected = %s
    WHERE trade_date = %s AND symbol = %s;
    """
    print('Updated Success')
    cursor.executemany(update_query, updates)
    conn.commit()

# Close DB connection
cursor.close()
conn.close()
