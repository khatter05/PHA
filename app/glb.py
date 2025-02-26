import pandas as pd


# market_data.py || websocket_handler.py
feedJson = {}
"""
feedjson={
    token = {
        'ltp' : last updated price,
        'tt' : timestamp
        }
}
"""
# websocket_handler.py
feed_opened = False  
websocket_connected = False 



nearest_value = 80



# trigger_handler.py
HEADERS = {
    'Content-Type': 'application/json'
}
TIMEOUT = 10



# market_data.py

#--------------------------------------------------------------
from utils import get_ltp, round_to_multiple

nifty_ltp = get_ltp('NIFTY INDEX')
nifty_ltp_rounded = round_to_multiple(nifty_ltp, 50)
print(f"Nifty LTP: {nifty_ltp}, Rounded: {nifty_ltp_rounded}")

# Replace the existing CE/PE array creation with this:
upper_strike = nifty_ltp_rounded + 600
lower_strike = nifty_ltp_rounded - 600

# Filter CE strikes within range
ce_strikes = ce_info[
    (ce_info['StrikePrice'] >= lower_strike) &
    (ce_info['StrikePrice'] <= upper_strike)
]
result_array_CE = ce_strikes.apply(lambda row: f"{row['Exchange']}|{row['Token']}", axis=1).to_list()

# Filter PE strikes within range
pe_strikes = pe_info[
    (pe_info['StrikePrice'] >= lower_strike) &
    (pe_info['StrikePrice'] <= upper_strike)
]
result_array_PE = pe_strikes.apply(lambda row: f"{row['Exchange']}|{row['Token']}", axis=1).to_list()

print(f"Monitoring CE strikes from {lower_strike} to {upper_strike}")
print(f"Total CE strikes: {len(result_array_CE)}")
print(f"Total PE strikes: {len(result_array_PE)}")








# Add these near the top with other global variables
position_lock = threading.Lock()
trigger_lock = threading.Lock()
last_trigger_time = {}  # To track last trigger time for each symbol
TRIGGER_COOLDOWN = 60  # 1 minute cooldown between triggers (changed from 300)

# Add at the top with other globals
order_processing_lock = threading.Lock()
processed_orders = set()  # To track already processed orders



df=pd.DataFrame

positions = pd.DataFrame(columns=['token', 'symbolname','option_type', 'buy_price', 'sell_price', 'buy_time', 'sell_time', 'state', 'option', 'qty', 'target', 'sl', 'trail'])


# Initialize an empty DataFrame to store trigger data
trigger_df = pd.DataFrame(columns=["symbolname","token","option_type","High", "Low", "TriggerCandle_Time", "State"])
# Add this at the top of the file with other global variables
processed_candles = set()  # To track which candles we've processed
# Add these near the top with other global variables
last_processed_interval = None  # To track the last 5-minute interval we processed


