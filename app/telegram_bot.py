import threading
import requests
import config
from typing import NoReturn

# Load configuration
CHAT_ID: str = config.chat_id 
BOT_TOKEN: str = config.bot_token 

def send_message1(msg: str) -> NoReturn:
    """Sends a message to a Telegram chat using the Telegram Bot API.
    
    Args:
        msg (str): The message text to be sent to the Telegram chat.
    
    Raises:
        Exception: If the request to Telegram API fails, an error is printed.
    """
    url: str = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data: dict[str, str] = {
        "chat_id": CHAT_ID,
        "text": msg
    }
    try:
        requests.post(url, data=data)
    except Exception as e:
        print(f"Failed to send message: {e}")

def send_message(msg: str) -> NoReturn:
    """Sends a message in a separate thread to avoid blocking the main script.
    
    Args:
        msg (str): The message text to be sent asynchronously.
    """
    thread = threading.Thread(target=send_message1, args=(msg,))
    thread.start()
