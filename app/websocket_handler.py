"""
websocket_handler.py - Handles real-time WebSocket communication.

This module initializes the WebSocket connection using the API client and defines
callbacks to process incoming market feed data and order updates. It uses global
variables imported from glb.py to share real-time data (feedJson) and connection status.
"""

from glb import feedJson, feed_opened, websocket_connected
from api_client import api_client
from datetime import datetime
import time

def event_handler_feed_update(tick_data):
    """
    Handle feed updates more gracefully.

    This function processes tick data received from the WebSocket, extracts the last
    traded price ('lp') and token ('tk'), and updates the global feedJson with the
    latest price and a timestamp. If a timestamp ('ft') is not provided, it uses the current time.

    Args:
        tick_data (dict): A dictionary containing tick data with keys 'lp', 'tk', and optionally 'ft'.
    """
    try:
        if 'lp' in tick_data and 'tk' in tick_data:
            # Get timestamp, default to current time if 'ft' is missing
            try:
                timest = datetime.fromtimestamp(int(tick_data.get('ft', time.time()))).isoformat()
            except (ValueError, TypeError):
                timest = datetime.now().isoformat()
            
            # Update feedJson with the tick data
            feedJson[tick_data['tk']] = {
                'ltp': float(tick_data['lp']),
                'tt': timest
            }
    except Exception as e:
        print(f"Error processing tick data: {str(e)}")

def event_handler_order_update(tick_data):
    """
    Handle order update events.

    Args:
        tick_data (dict): A dictionary containing order update information.
    """
    print(f"Order update {tick_data}")

def open_callback():
    """
    Callback function invoked when the WebSocket connection is opened.

    It sets the global flags feed_opened and websocket_connected to True.
    """
    global feed_opened, websocket_connected
    feed_opened = True
    if not websocket_connected:
        websocket_connected = True
        print("Websocket connected")

# Immediately start the WebSocket connection using the API client's start_websocket method.
# This call initiates the connection as soon as this module is imported.
api_client.api.start_websocket(order_update_callback=event_handler_order_update,
                               subscribe_callback=event_handler_feed_update,
                               socket_open_callback=open_callback)
