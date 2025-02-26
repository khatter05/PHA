import asyncio
import aiohttp
from telegram_bot import send_messagxe
from config import HEADERS, TIMEOUT
from file_manager import load_users_config  # Assuming load_users_config is defined in file_manager.py

async def trigger_webhook_for_user(session: aiohttp.ClientSession, user_name: str, config: dict, event_name: str) -> None:
    """
    Asynchronously triggers a webhook for a single user.

    This function checks if the specified event exists in the user's configuration. 
    If it does, it constructs a payload with the user's access token and the event name, 
    then sends a POST request to the webhook URL. It handles timeouts and network errors 
    by printing an error message and sending a Telegram alert.

    Args:
        session (aiohttp.ClientSession): The HTTP session for making asynchronous requests.
        user_name (str): The unique identifier for the user.
        config (dict): The user's configuration containing 'access_token' and 'webhooks'.
        event_name (str): The event name to trigger (e.g., "CE_Buy", "PE_Exit").

    Returns:
        None
    """
    if event_name not in config.get("webhooks", {}):
        error_msg = f"Invalid event: {event_name} for user {user_name}"
        print(error_msg)
        send_message(error_msg)
        return

    url = config["webhooks"][event_name]
    payload = {
        "access_token": config["access_token"],
        "alert_name": event_name
    }

    try:
        async with session.post(url, headers=HEADERS, json=payload, timeout=TIMEOUT) as response:
            if response.status == 200:
                success_msg = f"{event_name} Triggered Successfully for {user_name}!"
                print(success_msg)
            else:
                error_text = await response.text()
                error_msg = f"Failed to trigger {event_name} for {user_name}. Status: {response.status}, Response: {error_text}"
                print(error_msg)
                send_message(error_msg)
    except asyncio.TimeoutError:
        error_msg = f"Timeout error for {user_name} while triggering {event_name}. Webhook URL: {url}"
        print(error_msg)
        send_message(error_msg)
    except aiohttp.ClientError as e:
        error_msg = f"Network error for {user_name} while triggering {event_name}: {str(e)}. Webhook URL: {url}"
        print(error_msg)
        send_message(error_msg)
    except Exception as e:
        error_msg = f"Unexpected error for {user_name} while triggering {event_name}: {str(e)}"
        print(error_msg)
        send_message(error_msg)


async def trigger_webhook_async(event_name: str) -> None:
    """
    Asynchronously triggers webhooks for all users based on the given event name.
    
    This function loads user configuration from 'users.csv' using load_users_config().
    It then creates an asynchronous HTTP session and concurrently triggers webhooks 
    for each user by calling trigger_webhook_for_user. If the user configuration fails 
    to load or if an error occurs during webhook execution, it prints an error message 
    and sends a Telegram alert.
    
    Args:
        event_name (str): The name of the event that will be used to determine which webhook to trigger.
    
    Returns:
        None
    """
    users_config = load_users_config()
    
    if not users_config:
        error_msg = ("Failed to load users configuration. Check if users.csv exists "
                     "and is properly formatted.")
        print(error_msg)
        send_message(error_msg)
        return
    
    async with aiohttp.ClientSession() as session:
        tasks = []
        for user_name, config in users_config.items():
            task = trigger_webhook_for_user(session, user_name, config, event_name)
            tasks.append(task)
        
        try:
            # Execute all webhook calls concurrently
            await asyncio.gather(*tasks, return_exceptions=True)
        except Exception as e:
            error_msg = f"Error in webhook execution: {str(e)}"
            print(error_msg)
            send_message(error_msg)


def trigger_webhook(event_name: str) -> None:
    """
    Synchronously triggers a webhook for the given event using an asynchronous call.

    This function creates a new asyncio event loop, sets it as the current event loop,
    and runs the asynchronous function `trigger_webhook_async` with the provided event name.
    If an exception occurs during execution, it prints an error message and sends a Telegram alert.

    Args:
        event_name (str): The name of the event triggering the webhook.

    Returns:
        None
    """
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(trigger_webhook_async(event_name))
    except Exception as e:
        error_msg = f"Critical error in webhook system: {str(e)}"
        print(error_msg)
        send_message(error_msg)
    finally:
        loop.close()


def trigger_b(h: str) -> None:
    """
    Triggers a BUY event by appending '_Buy' to the given event name and calling trigger_webhook.

    Args:
        h (str): The base event name (typically representing an option type or trade signal).

    Returns:
        None
    """
    try:
        print(f"{h}_Buy")
        trigger_webhook(f"{h}_Buy")
    except Exception as e:
        print(f"Error in trigger_b: {e}")
        send_message(f"Error triggering {h}_Buy: {e}")


def trigger_s(h: str) -> None:
    """
    Triggers an EXIT event by appending '_Exit' to the given event name and calling trigger_webhook.

    Args:
        h (str): The base event name (typically representing an option type or trade signal).

    Returns:
        None
    """
    try:
        print(f"{h}_Exit")
        trigger_webhook(f"{h}_Exit")
    except Exception as e:
        print(f"Error in trigger_s: {e}")
        send_message(f"Error triggering {h}_Exit: {e}")
