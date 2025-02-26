from api_helper import ShoonyaApiPy
import yaml
import datetime
import timeit
import pyotp
import json
import pandas as pd
import numpy as np
import requests
import logging
import threading
import time
from datetime import timedelta
import pandas as pd
import ssl
import asyncio
import aiohttp
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
import os
import sys

from app.utils import load_users_config 
from app.message import send_message 
from app.glb import 



"""Handles Shoonya API authentication and requests."""

from api_helper import ShoonyaApiPy
import pyotp
import config


class APIClient:
    """Singleton class for Shoonya API authentication and requests."""

    _instance: "APIClient" = None

    def __new__(cls) -> "APIClient":
        """Creates a single instance of APIClient.
        
        Returns:
            APIClient: A single instance of the APIClient class.
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.api = ShoonyaApiPy()
            cls._instance.login()
        return cls._instance

    def login(self) -> None:
        """Logs into the Shoonya API."""
        self.api.login(
            userid=config.UID,
            password=config.PWD,
            twoFA=pyotp.TOTP(config.TOKEN).now(),
            vendor_code=config.VC,
            api_secret=config.APP_KEY,
            imei=config.IMEI,
        )
        print("✅ Logged into Shoonya API successfully.")

    def get_ltp(self, stockname: str) -> float:
        """Fetches Last Traded Price (LTP) for a stock.
        
        Args:
            stockname (str): The name of the stock to fetch the LTP for.
        
        Returns:
            float: The last traded price of the stock.
        """
        ret = self.api.searchscrip(exchange="NSE", searchtext=stockname)
        token: str = ret["values"][0]["token"]
        res = self.api.get_quotes(exchange="NSE", token=token)
        return float(res["lp"])


# Singleton instance
api_client = APIClient()



api = ShoonyaApiPy()

with open("config.yaml", "r") as file:
    config = yaml.safe_load(file)

uid = config['credentials']['uid']
pwd = config['credentials']['pwd']
token = config['credentials']['token']
vc = config['credentials']['vc']
app_key = config['credentials']['app_key']
imei = config['credentials']['imei']

ret = api.login(userid=uid, password=pwd, twoFA=pyotp.TOTP(token).now(), vendor_code=vc, api_secret=app_key, imei=imei)
print(ret)

send_message("GoldenSniper Algo Started")



def event_handler_feed_update(tick_data):
    """Handle feed updates more gracefully"""
    try:
        if 'lp' in tick_data and 'tk' in tick_data:
            # Get timestamp, default to current time if 'ft' is missing
            try:
                timest = datetime.fromtimestamp(int(tick_data.get('ft', time.time()))).isoformat()
            except (ValueError, TypeError):
                timest = datetime.now().isoformat()
 # feedjson global issue-- needs review !!!!           
            # Update feedJson with the tick data
            feedJson[tick_data['tk']] = {
                'ltp': float(tick_data['lp']),
                'tt': timest
            }
    except Exception as e:
        print(f"Error processing tick data: {str(e)}")

def event_handler_order_update(tick_data):
    print(f"Order update {tick_data}")

fro app.glb import feed_opened

def open_callback():
    #global feed_opened, websocket_connected
    glb.feed_opened = True
    if not glb.websocket_connected:
        glb.websocket_connected = True
        print("Websocket connected")

#Review
# Replace the initial websocket setup section
api.start_websocket(order_update_callback=event_handler_order_update,
                   subscribe_callback=event_handler_feed_update,
                   socket_open_callback=open_callback)


# Wait for initial connection
retry_count = 0
while not glb.feed_opened and retry_count < 10:
    time.sleep(1)
    retry_count += 1

if not glb.feed_opened:
    print("Failed to establish websocket connection")
    sys.exit(1)

# Initial subscriptions - do these only once
try:
    api.subscribe('NSE|26000')
    api.subscribe(result_array_CE)
    api.subscribe(result_array_PE)
    print("Initial subscriptions completed")
except Exception as e:
    print(f"Error in initial subscription: {e}")

time.sleep(5)
print(f"Feed JSON: {glb.feedJson}")

# Start monitoring in a separate thread
threading.Thread(target=monitor_positions, daemon=True).start()

ce_strike=get_ce_pe_values(nearest_value,"CE")
pe_strike=get_ce_pe_values(nearest_value,"PE")

print(f"CE Strike: {ce_strike}, PE Strike: {pe_strike}")
strikes=[]
strikes.append(ce_strike)
strikes.append(pe_strike)

print(f"Strikes: {strikes}")


