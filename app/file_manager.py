import time
import pandas as pd
from typing import Dict, Any, Optional

# Modify the load_users_config function to cache the results
_users_config_cache: Optional[Dict[str, Any]] = None
_last_cache_time: float = 0
CACHE_DURATION: int = 300  # Cache duration in seconds (5 minutes)

def load_users_config() -> Dict[str, Dict[str, Any]]:
    """Loads user configuration from 'users.csv' and caches the results.
    
    The function reads a CSV file named 'users.csv', extracts user credentials and webhook URLs, and 
    returns a structured dictionary. The dictionary follows this structure:
    
    ```python
    {
        "username1": {
            "access_token": "token_value",
            "webhooks": {
                "CE_Buy": "url1",
                "CE_Exit": "url2",
                "PE_Buy": "url3",
                "PE_Exit": "url4"
            }
        },
        "username2": { ... },
        ...
    }
    ```
    
    Returns:
        Dict[str, Dict[str, Any]]: A dictionary where keys are usernames (str), and values are 
        dictionaries containing an 'access_token' (str) and a nested 'webhooks' dictionary with event-action mappings.
    """
    global _users_config_cache, _last_cache_time
    current_time: float = time.time()
    
    # Return cached config if it's still valid
    if _users_config_cache and (current_time - _last_cache_time) < CACHE_DURATION:
        return _users_config_cache
    
    try:
        users_df: pd.DataFrame = pd.read_csv('users.csv')
        users_config: Dict[str, Dict[str, Any]] = {}
        
        for _, row in users_df.iterrows():
            users_config[row['name']] = {
                'access_token': row['access_token'],
                'webhooks': {
                    'CE_Buy': row['ce_buy'],
                    'CE_Exit': row['ce_exit'],
                    'PE_Buy': row['pe_buy'],
                    'PE_Exit': row['pe_exit']
                }
            }
        
        _users_config_cache = users_config
        _last_cache_time = current_time
        return users_config
    except Exception as e:
        print(f"Error loading users config: {e}")
        return {}
