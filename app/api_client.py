
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