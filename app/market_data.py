"""
market_data.py - Fetches and processes market data.
"""

import pandas as pd
from datetime import datetime, timedelta
from api_client import api_client
from glb import feedJson  # Importing feedJson directly

# Load market data
symbolDf = pd.read_csv("https://api.shoonya.com/NFO_symbols.txt.zip")
symbolDf["Expiry"] = pd.to_datetime(symbolDf["Expiry"]).apply(lambda x: x.date())
ocdf = symbolDf[symbolDf.Symbol == "NIFTY"].sort_values(by="Expiry")
latest_expiry = ocdf.head(1)["Expiry"].values[0]

# Extract CE/PE information
ce_info = ocdf[(ocdf["Expiry"] == latest_expiry) & (ocdf["OptionType"] == "CE")]
pe_info = ocdf[(ocdf["Expiry"] == latest_expiry) & (ocdf["OptionType"] == "PE")]

def get_ce_pe_values(premium, option):
    """Finds the closest CE/PE token based on the given premium.

    Args:
        premium (float): The target premium value.
        option (str): "CE" for Call, "PE" for Put.

    Returns:
        str: The closest matching symbol name, or None if not found.
    """
    global pe_info, ce_info, feedJson
    info = ce_info if option == "CE" else pe_info if option == "PE" else None
    if info is None:
        print("Invalid option type provided")
        return None

    target_ltp = premium
    closest_token = None
    closest_diff = float("inf")
    
    print(f"Searching for {option} strike with premium close to {premium}")
    
    for token in info["Token"]:
        str_token = str(token)
        if str_token in feedJson:
            current_diff = abs(feedJson[str_token]["ltp"] - target_ltp)
            if current_diff < closest_diff:
                closest_diff = current_diff
                closest_token = str_token
                
    if closest_token is not None:
        symbol_name = info[info["Token"] == int(closest_token)]["TradingSymbol"].values[0]
        strike_price = info[info["Token"] == int(closest_token)]["StrikePrice"].values[0]
        ltp = feedJson[closest_token]["ltp"]
        print(f"Selected {option} strike: {symbol_name}, Strike Price: {strike_price}, LTP: {ltp}")
        return symbol_name
    else:
        print(f"No suitable {option} strike found")
        return None

def get_time_series(exchange, token, days, interval):
    """Fetches historical price data for a stock.

    Args:
        exchange (str): The exchange code (e.g., "NSE").
        token (str): The token ID for the stock.
        days (int): Number of past days to retrieve.
        interval (str): Time interval (e.g., "5minute", "15minute").

    Returns:
        pd.DataFrame: DataFrame containing historical price data.
    """
    now = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    prev_day = now - timedelta(days=days)
    prev_day_timestamp = prev_day.timestamp()
    ret = api_client.api.get_time_price_series(
        exchange=exchange,
        token=token,
        starttime=prev_day_timestamp,
        interval=interval
    )
    if ret:
        return pd.DataFrame(ret)
    else:
        print("No Data for the given exchange, token, days and interval")
        return pd.DataFrame()


# Assume that 'api' and 'get_time_series' are available in the scope,
# either via a direct import or defined earlier in your code.

def dt_update(stock: str) -> pd.DataFrame:
    """
    Updates and returns a 5-minute resampled DataFrame for the given stock.

    This function performs the following steps:
      1. Uses `api.searchscrip` on the 'NFO' exchange to search for the given stock,
         and retrieves the token from the first result.
      2. Calls `get_time_series('NFO', token, 4, 1)` to fetch historical time series data.
      3. If the resulting DataFrame is not empty:
         - Selects the columns ['time', 'into', 'inth', 'intl', 'intc'].
         - Renames the columns:
             'intc' -> 'Close',
             'intl' -> 'Low',
             'inth' -> 'High',
             'into' -> 'Open',
             'time' -> 'Datetime'.
         - Converts the 'Datetime' column to datetime objects (coercing errors).
         - Drops any rows with missing values.
         - Sorts the DataFrame by 'Datetime' in ascending order and resets the index.
         - Sets 'Datetime' as the index.
         - Resamples the DataFrame into 5-minute intervals, aggregating:
             'Open' as the first value,
             'High' as the maximum,
             'Low' as the minimum,
             'Close' as the last value.
         - Drops any rows with missing values after resampling and resets the index.
         - Returns the resampled DataFrame.
      4. If the DataFrame is empty, it simply returns the empty DataFrame.

    Args:
        stock (str): The stock symbol to search for.

    Returns:
        pd.DataFrame: The processed 5-minute resampled DataFrame, or the original (possibly empty) DataFrame.
    """
    global df
    ret = api.searchscrip(exchange='NFO', searchtext=stock)
    token = ret['values'][0]['token']
    df = get_time_series('NFO', token, 4, 1)
    
    if not df.empty:
        df = df[['time', 'into', 'inth', 'intl', 'intc']]
        df.rename(columns={'intc': 'Close', 'intl': 'Low', 'inth': 'High', 'into': 'Open', 'time': 'Datetime'}, inplace=True)
        df['Datetime'] = pd.to_datetime(df['Datetime'], errors='coerce')
        df.dropna(inplace=True)
        df = df.sort_values(by='Datetime', ascending=True).reset_index(drop=True)
        df.set_index('Datetime', inplace=True)
        df_5min = df.resample('5T').agg({
            'Open': 'first',
            'High': 'max',
            'Low': 'min',
            'Close': 'last'
        }).dropna().reset_index()
        
        return df_5min
    return df
