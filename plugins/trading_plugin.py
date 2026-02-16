import logging
from typing import Dict, List, Any, Optional, Tuple, Union
import copy
import random
from datetime import datetime, time, timedelta

logger = logging.getLogger(__name__)
import traceback


CURRENT_TIME = datetime(2024, 9, 1, 10, 30)

# Default state for the trading system
DEFAULT_STATE = {
    "orders": {
        12345: {
            "id": 12345,
            "order_type": "Buy",
            "symbol": "AAPL",
            "price": 210.65,
            "amount": 10,
            "status": "Completed",
        },
        12446: {
            "id": 12446,
            "order_type": "Sell",
            "symbol": "GOOG",
            "price": 2840.56,
            "amount": 5,
            "status": "Pending",
        },
    },
    "account_info": {
        "account_id": 12345,
        "balance": 10000.0,
        "binding_card": 1974202140965533,
    },
    "authenticated": False,
    "market_status": "Closed",
    "order_counter": 12446,
    "stocks": {
        "AAPL": {
            "price": 227.16,
            "percent_change": 0.17,
            "volume": 2.552,
            "MA(5)": 227.11,
            "MA(20)": 227.09,
        },
        "GOOG": {
            "price": 2840.34,
            "percent_change": 0.24,
            "volume": 1.123,
            "MA(5)": 2835.67,
            "MA(20)": 2842.15,
        },
        "TSLA": {
            "price": 667.92,
            "percent_change": -0.12,
            "volume": 1.654,
            "MA(5)": 671.15,
            "MA(20)": 668.20,
        },
        "MSFT": {
            "price": 310.23,
            "percent_change": 0.09,
            "volume": 3.234,
            "MA(5)": 309.88,
            "MA(20)": 310.11,
        },
        "NVDA": {
            "price": 220.34,
            "percent_change": 0.34,
            "volume": 1.234,
            "MA(5)": 220.45,
            "MA(20)": 220.67,
        },
        "ALPH": {
            "price": 1320.45,
            "percent_change": -0.08,
            "volume": 1.567,
            "MA(5)": 1321.12,
            "MA(20)": 1325.78,
        },
        "OMEG": {
            "price": 457.23,
            "percent_change": 0.12,
            "volume": 2.345,
            "MA(5)": 456.78,
            "MA(20)": 458.12,
        },
        "QUAS": {
            "price": 725.89,
            "percent_change": -0.03,
            "volume": 1.789,
            "MA(5)": 726.45,
            "MA(20)": 728.00,
        },
        "NEPT": {
            "price": 88.34,
            "percent_change": 0.19,
            "volume": 0.654,
            "MA(5)": 88.21,
            "MA(20)": 88.67,
        },
        "SYNX": {
            "price": 345.67,
            "percent_change": 0.11,
            "volume": 2.112,
            "MA(5)": 345.34,
            "MA(20)": 346.12,
        },
        "ZETA": {
            "price": 22.09,
            "percent_change": -0.05,
            "volume": 0.789,
            "MA(5)": 22.12,
            "MA(20)": 22.34,
        },
    },
    "watch_list": ["NVDA"],
    "transaction_history": [],
    "random_seed": 1053520,
}



class TradingBot:
    """
    A class representing a trading bot for executing stock trades and managing a trading account.
    Authentication and account management are handled internally.
    """
    
    def __init__(self):
        """Initialize the TradingBot instance with default state."""
        self.orders = {}
        self.account_info = {}
        self.market_status = "Closed"
        self.order_counter = 0
        self.stocks = {}
        self.watch_list = []
        self.transaction_history = []
        self._api_description = "This tool belongs to the trading system, which allows users to trade stocks, manage their account, and view stock information."
        self._random = random.Random(1053520)
        
        # Load default state
        self._load_scenario(DEFAULT_STATE)

    def _load_scenario(self, scenario: dict) -> None:
        """
        Load a scenario into the TradingBot.
        
        Args:
            scenario (dict): A scenario dictionary containing data to load.
        """
        DEFAULT_STATE_COPY = copy.deepcopy(DEFAULT_STATE)
        self.orders = scenario.get("orders", DEFAULT_STATE_COPY["orders"])
        # Convert all string keys that can be interpreted as integers to integer keys
        self.orders = {
            int(k) if isinstance(k, str) and k.isdigit() else k: v
            for k, v in self.orders.items()
        }
        self.account_info = scenario.get("account_info", DEFAULT_STATE_COPY["account_info"])
        self.market_status = scenario.get("market_status", DEFAULT_STATE_COPY["market_status"])
        self.order_counter = scenario.get("order_counter", DEFAULT_STATE_COPY["order_counter"])
        self.stocks = scenario.get("stocks", DEFAULT_STATE_COPY["stocks"])
        self.watch_list = scenario.get("watch_list", DEFAULT_STATE_COPY["watch_list"])
        self.transaction_history = scenario.get("transaction_history", DEFAULT_STATE_COPY["transaction_history"])
        self._random = random.Random(scenario.get("random_seed", DEFAULT_STATE_COPY["random_seed"]))

    def _generate_transaction_timestamp(self) -> str:
        """
        Generate a timestamp for a transaction.
        
        Returns:
            timestamp (str): A formatted timestamp string.
        """
        # Define the start and end dates for the range
        start_date = CURRENT_TIME
        end_date = CURRENT_TIME + timedelta(days=1)

        start_timestamp = int(start_date.timestamp())
        end_timestamp = int(end_date.timestamp())

        # Generate a random timestamp within the range
        random_timestamp = self._random.randint(start_timestamp, end_timestamp)

        # Convert the random timestamp to a datetime object
        random_date = datetime.fromtimestamp(random_timestamp)

        return random_date.strftime("%Y-%m-%d %H:%M:%S")

    def get_current_time(self) -> Dict[str, str]:
        """
        Get the current time.
        
        Returns:
            current_time (str): Current time in HH:MM AM/PM format.
        """
        return {"current_time": CURRENT_TIME.strftime("%I:%M %p")}

    def update_market_status(self, current_time_str: str) -> Dict[str, str]:
        """
        Update the market status based on the current time.
        
        Args:
            current_time_str (str): Current time in HH:MM AM/PM format.
            
        Returns:
            status (str): Status of the market. [Enum]: ["Open", "Closed"]
        """
        market_open_time = time(9, 30)  # Market opens at 9:30 AM
        market_close_time = time(16, 0)  # Market closes at 4:00 PM

        try:
            current_time = datetime.strptime(current_time_str, "%I:%M %p").time()
        except ValueError:
            return {"error": f"Invalid time format: {current_time_str}. Use HH:MM AM/PM format."}

        if market_open_time <= current_time <= market_close_time:
            self.market_status = "Open"
            return {"status": "Open"}
        else:
            self.market_status = "Closed"
            return {"status": "Closed"}

    def get_symbol_by_name(self, name: str) -> Dict[str, str]:
        """
        Get the symbol of a stock by company name.
        
        Args:
            name (str): Name of the company.
            
        Returns:
            symbol (str): Symbol of the stock or "Stock not found" if not available.
        """
        symbol_map =  {
            "Apple": "AAPL",
            "Google": "GOOG",
            "Tesla": "TSLA",
            "Microsoft": "MSFT",
            "Nvidia": "NVDA",
            "Zeta Corp": "ZETA",
            "Alpha Tech": "ALPH",
            "Omega Industries": "OMEG",
            "Quasar Ltd.": "QUAS",
            "Neptune Systems": "NEPT",
            "Synex Solutions": "SYNX",
            "Amazon": "AMZN",
        }

        return {"symbol": symbol_map.get(name, "Stock not found")}

    def get_stock_info(self, symbol: str) -> Dict[str, Union[float, int, str]]:
        """
        Get the details of a stock.
        
        Args:
            symbol (str): Symbol that uniquely identifies the stock.
            
        Returns:
            price (float): Current price of the stock.
            percent_change (float): Percentage change in stock price.
            volume (float): Trading volume of the stock.
            MA(5) (float): 5-day Moving Average of the stock.
            MA(20) (float): 20-day Moving Average of the stock.
        """
        if symbol not in self.stocks:
            return {"error": f"Stock with symbol '{symbol}' not found."}
        return self.stocks[symbol]

    def get_order_details(self, order_id: int) -> Dict[str, Union[str, float, int]]:
        """
        Get the details of an order.
        
        Args:
            order_id (int): ID of the order.
            
        Returns:
            id (int): ID of the order.
            order_type (str): Type of the order.
            symbol (str): Symbol of the stock in the order.
            price (float): Price at which the order was placed.
            amount (int): Number of shares in the order.
            status (str): Current status of the order. [Enum]: ["Open", "Pending", "Completed", "Cancelled"]
        """
        order_id = int(order_id)
        
        if order_id not in self.orders:
            return {
                "error": f"Order with ID {order_id} not found. "
                + "Available order IDs: " + str(list(self.orders.keys()))
            }
        return self.orders[order_id]

    def cancel_order(self, order_id: int) -> Dict[str, Union[int, str]]:
        """
        Cancel an order.
        
        Args:
            order_id (int): ID of the order to cancel.
            
        Returns:
            order_id (int): ID of the cancelled order.
            status (str): New status of the order after cancellation attempt.
        """
        if order_id not in self.orders:
            return {"error": f"Order with ID {order_id} not found."}
        if self.orders[order_id]["status"] == "Completed":
            return {"error": f"Cannot cancel order {order_id}. Order is already completed."}
        
        self.orders[order_id]["status"] = "Cancelled"
        return {"order_id": order_id, "status": "Cancelled"}

    def place_order(
        self, order_type: str, symbol: str, price: float, amount: int
    ) -> Dict[str, Union[int, str, float]]:
        """
        Place an order for a stock (buy or sell it.)
        
        Args:
            order_type (str): Type of the order (Buy/Sell).
            symbol (str): Symbol of the stock to trade.
            price (float): Price at which to place the order.
            amount (int): Number of shares to trade.
            
        Returns:
            order_id (int): ID of the newly placed order.
            order_type (str): Type of the order (Buy/Sell).
            status (str): Initial status of the order.
            price (float): Price at which the order was placed.
            amount (int): Number of shares in the order.
        """
        if symbol not in self.stocks:
            return {"error": f"Invalid stock symbol: {symbol}"}
        if price <= 0 or amount <= 0:
            return {"error": "Price and amount must be positive values."}
        
        price = float(price)
        
        order_id = self.order_counter

        self.order_counter += 1
        
        self.orders[order_id] = {
            "id": order_id,
            "order_type": order_type,
            "symbol": symbol,
            "price": price,
            "amount": amount,
            "status": "Open",
        }
        
        # Return the status as "Pending" to indicate that the order has been placed but not yet executed
        return {
            "order_id": order_id,
            "order_type": order_type,
            "status": "Pending",
            "price": price,
            "amount": amount,
        }

    def make_transaction(self, xact_type: str, amount: float) -> Dict[str, Union[str, float]]:
        """
        Make a deposit or withdrawal based on specified amount.
        Uses the internal account automatically.
        
        Args:
            xact_type (str): Transaction type (deposit or withdrawal).
            amount (float): Amount to deposit or withdraw.
            
        Returns:
            status (str): Status of the transaction.
            new_balance (float): Updated account balance after the transaction.
        """
        if self.market_status != "Open":
            return {"error": "Market is closed. Transactions are not allowed."}
        if amount <= 0:
            return {"error": "Transaction amount must be positive."}

        if xact_type == "deposit":
            self.account_info["balance"] += amount
            self.transaction_history.append(
                {
                    "type": "deposit",
                    "amount": amount,
                    "timestamp": self._generate_transaction_timestamp(),
                }
            )
            return {
                "status": "Deposit successful",
                "new_balance": self.account_info["balance"],
            }
        elif xact_type == "withdrawal":
            if amount > self.account_info["balance"]:
                return {"error": "Insufficient funds for withdrawal."}
            self.account_info["balance"] -= amount
            self.transaction_history.append(
                {
                    "type": "withdrawal",
                    "amount": amount,
                    "timestamp": self._generate_transaction_timestamp(),
                }
            )
            return {
                "status": "Withdrawal successful",
                "new_balance": self.account_info["balance"],
            }
        return {"error": "Invalid transaction type. Use 'deposit' or 'withdrawal'."}

    def get_account_info(self) -> Dict[str, Union[int, float]]:
        """
        Get account information.
        
        Returns:
            account_id (int): ID of the account.
            balance (float): Current balance of the account.
            binding_card (int): Card number associated with the account.
        """
        return self.account_info

    def fund_account(self, amount: float) -> Dict[str, Union[str, float]]:
        """
        Fund the account with the specified amount.
        
        Args:
            amount (float): Amount to fund the account with.
            
        Returns:
            status (str): Status of the funding operation.
            new_balance (float): Updated account balance after funding.
        """
        if amount <= 0:
            return {"error": "Funding amount must be positive."}
        
        self.account_info["balance"] += amount
        self.transaction_history.append(
            {"type": "deposit", "amount": amount, "timestamp": self._generate_transaction_timestamp()}
        )
        return {
            "status": "Account funded successfully",
            "new_balance": self.account_info["balance"],
        }

    def remove_stock_from_watchlist(self, symbol: str) -> Dict[str, str]:
        """
        Remove a stock from the watchlist.
        
        Args:
            symbol (str): Symbol of the stock to remove.
            
        Returns:
            status (str): Status of the removal operation.
        """
        if symbol not in self.watch_list:
            return {"error": f"Stock {symbol} not found in watchlist."}
        
        self.watch_list.remove(symbol)
        return {"status": f"Stock {symbol} removed from watchlist successfully."}

    def get_watchlist(self) -> Dict[str, List[str]]:
        """
        Get the watchlist.
        
        Returns:
            watchlist (List[str]): List of stock symbols in the watchlist.
        """
        return {"watchlist": self.watch_list}

    def get_order_history(self) -> Dict[str, List[int]]:
        """
        Get the stock order ID history.
        
        Returns:
            order_history (List[int]): List of order IDs in the order history.
        """
        return {"history": list(self.orders.keys())}

    def get_transaction_history(
        self, start_date: Optional[str] = None, end_date: Optional[str] = None
    ) -> Dict[str, List[Dict[str, Union[str, float]]]]:
        """
        Get the transaction history within a specified date range.
        
        Args:
            start_date (str): [Optional] Start date for the history (format: 'YYYY-MM-DD').
            end_date (str): [Optional] End date for the history (format: 'YYYY-MM-DD').
            
        Returns:
            transaction_history (List[Dict]): List of transactions within the specified date range.
                - type (str): Type of transaction. [Enum]: ["deposit", "withdrawal"]
                - amount (float): Amount involved in the transaction.
                - timestamp (str): Timestamp of the transaction, formatted as 'YYYY-MM-DD HH:MM:SS'.
        """
        if start_date:
            try:
                start = datetime.strptime(start_date, "%Y-%m-%d")
            except ValueError:
                return {"error": f"Invalid start_date format: {start_date}. Use YYYY-MM-DD."}
        else:
            start = datetime.min

        if end_date:
            try:
                end = datetime.strptime(end_date, "%Y-%m-%d")
            except ValueError:
                return {"error": f"Invalid end_date format: {end_date}. Use YYYY-MM-DD."}
        else:
            end = datetime.max

        filtered_history = []
        for transaction in self.transaction_history:
            try:
                tx_time = datetime.strptime(transaction["timestamp"], "%Y-%m-%d %H:%M:%S")
                if start <= tx_time <= end:
                    filtered_history.append(transaction)
            except (ValueError, KeyError):
                # Skip malformed transaction entries
                continue

        return {"transaction_history": filtered_history}

    def update_stock_price(
        self, symbol: str, new_price: float
    ) -> Dict[str, Union[str, float]]:
        """
        Update the price of a stock.
        
        Args:
            symbol (str): Symbol of the stock to update.
            new_price (float): New price of the stock.
            
        Returns:
            symbol (str): Symbol of the updated stock.
            old_price (float): Previous price of the stock.
            new_price (float): Updated price of the stock.
        """
        if symbol not in self.stocks:
            return {"error": f"Stock with symbol '{symbol}' not found."}
        if new_price <= 0:
            return {"error": "New price must be a positive value."}

        old_price = self.stocks[symbol]["price"]
        self.stocks[symbol]["price"] = new_price
        
        # Calculate percent change
        if old_price > 0:
            self.stocks[symbol]["percent_change"] = ((new_price - old_price) / old_price) * 100
        else:
            self.stocks[symbol]["percent_change"] = 0.0

        return {"symbol": symbol, "old_price": old_price, "new_price": new_price}

    def get_available_stocks(self, sector: str) -> Dict[str, List[str]]:
        """
        Get a list of stock symbols in the given sector.
        
        Args:
            sector (str): The sector to retrieve stocks from (e.g., 'Technology').
            
        Returns:
            stock_list (List[str]): List of stock symbols in the specified sector.
        """
        sector_map = {
            "Technology": ["AAPL", "GOOG", "MSFT", "NVDA"],
            "Automobile": ["TSLA"],
            "Healthcare": ["NEPT"],
            "Finance": ["ALPH"],
            "Energy": ["OMEG"],
        }
        return {"stock_list": sector_map.get(sector, [])}

    def filter_stocks_by_price(
        self, stocks: List[str], min_price: float, max_price: float
    ) -> Dict[str, List[str]]:
        """
        Filter stocks based on a price range.
        
        Args:
            stocks (List[str]): List of stock symbols to filter.
            min_price (float): Minimum stock price.
            max_price (float): Maximum stock price.
            
        Returns:
            filtered_stocks (List[str]): Filtered list of stock symbols within the price range.
        """
        if min_price < 0 or max_price < 0:
            return {"error": "Price values must be non-negative."}
        if min_price > max_price:
            return {"error": "Minimum price cannot be greater than maximum price."}
            
        filtered_stocks = []
        for symbol in stocks:
            if symbol in self.stocks:
                price = self.stocks[symbol].get("price", 0)
                if min_price <= price <= max_price:
                    filtered_stocks.append(symbol)
                    
        return {"filtered_stocks": filtered_stocks}

    def add_to_watchlist(self, stock: str) -> Dict[str, Union[List[str], str]]:
        """
        Add a stock to the watchlist.
        
        Args:
            stock (str): the stock symbol to add to the watchlist.
            
        Returns:
            watchlist (List[str]): the updated watchlist after adding the stock.
        """
        if stock not in self.stocks:
            return {"error": f"Stock {stock} not found."}
        
        if stock not in self.watch_list:
            self.watch_list.append(stock)
            
        return {"watchlist": self.watch_list}

    def notify_price_change(self, stocks: List[str], threshold: float) -> Dict[str, str]:
        """
        Notify if there is a significant price change in the stocks.
        
        Args:
            stocks (List[str]): List of stock symbols to check.
            threshold (float): Percentage change threshold to trigger a notification.
            
        Returns:
            notification (str): Notification message about the price changes.
        """
        if threshold < 0:
            return {"error": "Threshold must be non-negative."}
            
        changed_stocks = []
        for symbol in stocks:
            if symbol in self.stocks:
                percent_change = abs(self.stocks[symbol].get("percent_change", 0))
                if percent_change >= threshold:
                    changed_stocks.append(symbol)

        if changed_stocks:
            return {"notification": f"Stocks {', '.join(changed_stocks)} have significant price changes."}
        else:
            return {"notification": "No significant price changes in the selected stocks."}


# Import the base plugin here to avoid circular imports
from plugins.base_plugin import BasePlugin


class TradingPlugin(BasePlugin):
    """Plugin for stock trading operations.
    
    This plugin provides tools for stock trading, market data, and account management
    with dynamic domain updates and proper type casting. Authentication is handled
    internally and account management is simplified.
    """
    
    def __init__(self):
        """Initialize the trading plugin."""
        super().__init__()

        self.trading_bot = TradingBot()
        self._name = "trading"
        self._description = "Plugin for stock trading operations"
        self._tools = self._generate_tool_definitions()
        
        # Cache for dynamic domains - invalidated when state changes
        self._domain_cache = None
        self._state_changing_operations = {
            'place_order', 'cancel_order', 'make_transaction', 'fund_account',
            'remove_stock_from_watchlist', 'add_to_watchlist', 'update_stock_price'
        }
    
    @property
    def name(self) -> str:
        """Get the name of the plugin."""
        return self._name
    
    @property
    def description(self) -> str:
        """Get the description of the plugin."""
        return self._description
    
    def _generate_tool_definitions(self) -> List[Dict[str, Any]]:
        """Generate tool definitions for the trading plugin."""
        return [
            {
                "name": "get_current_time",
                "description": "Get the current market time in HH:MM AM/PM format. Use this to check trading hours and determine if the market is open for operations.",
                "arguments": []
            },
            {
                "name": "update_market_status",
                "description": "Update and check market status based on current time. Market is open 9:30 AM - 4:00 PM. Many trading operations require the market to be open.",
                "arguments": [
                    {
                        "name": "current_time_str",
                        "description": "Current time in HH:MM AM/PM format (e.g., '10:30 AM', '3:45 PM'). Must include AM/PM and use 12-hour format with colon separator.",
                        "domain": {
                            "type": "string",
                            "importance": 0.8
                        },
                        "required": True
                    }
                ]
            },
            {
                "name": "get_symbol_by_name",
                "description": "Look up a stock symbol using the company name. Use this when you know the company name but need the trading symbol for other operations.",
                "arguments": [
                    {
                        "name": "name",
                        "description": "Company name to look up (e.g., 'Apple', 'Google', 'Microsoft'). Must match exact company names in the system database for successful lookup.",
                        "domain": {
                            "type": "string",
                            "importance": 0.9
                        },
                        "required": True
                    }
                ]
            },
            {
                "name": "get_stock_info",
                "description": "Get detailed information about a stock including current price, percentage change, volume, and moving averages. Essential for making informed trading decisions.",
                "arguments": [
                    {
                        "name": "symbol",
                        "description": "Stock symbol to get information for (e.g., 'AAPL', 'GOOG', 'TSLA'). Must be a valid symbol available in the trading system. Use get_symbol_by_name if you only know the company name.",
                        "domain": {
                            "type": "string",
                            "importance": 0.9,
                            "data_dependent": True
                        },
                        "required": True
                    }
                ]
            },
            {
                "name": "get_order_details",
                "description": "Retrieve detailed information about a specific order including status, price, amount, and order type. Use the order ID returned when the order was placed.",
                "arguments": [
                    {
                        "name": "order_id",
                        "description": "Unique order identifier (integer) returned when order was placed. Must be an existing order ID in the system (typically 5-6 digit numbers).",
                        "domain": {
                            "type": "numeric_range",
                            "values": [1, 100000],
                            "importance": 0.9,
                            "data_dependent": True
                        },
                        "required": True
                    }
                ]
            },
            {
                "name": "cancel_order",
                "description": "Cancel an existing order that hasn't been completed yet. Cannot cancel orders that are already completed. Returns updated order status.",
                "arguments": [
                    {
                        "name": "order_id",
                        "description": "Unique order identifier to cancel. Must be an existing order that is not already completed. Use get_order_details to check order status first.",
                        "domain": {
                            "type": "numeric_range",
                            "values": [1, 100000],
                            "importance": 0.9,
                            "data_dependent": True
                        },
                        "required": True
                    }
                ]
            },
            {
                "name": "place_order",
                "description": "Place a new buy or sell order for a stock. This creates the order but doesn't immediately execute it. Returns an order ID for tracking. Ensure you have sufficient account balance for buy orders.",
                "arguments": [
                    {
                        "name": "order_type",
                        "description": "Type of order to place. 'Buy' to purchase shares, 'Sell' to dispose of shares. Case-sensitive - use exact capitalization 'Buy' or 'Sell'.",
                        "domain": {
                            "type": "finite",
                            "values": ["Buy", "Sell"],
                            "importance": 0.9
                        },
                        "required": True
                    },
                    {
                        "name": "symbol",
                        "description": "Stock symbol to trade (e.g., 'AAPL', 'MSFT'). Must be a valid symbol available in the system. Check with get_stock_info first to verify symbol exists.",
                        "domain": {
                            "type": "string",
                            "importance": 0.9,
                            "data_dependent": True
                        },
                        "required": True
                    },
                    {
                        "name": "price",
                        "description": "Price per share for the order in USD (0.01-10,000). This is your limit price - the maximum you'll pay for a buy order or minimum you'll accept for a sell order.",
                        "domain": {
                            "type": "numeric_range",
                            "values": [0.01, 10000.0],
                            "importance": 0.8
                        },
                        "required": True
                    },
                    {
                        "name": "amount",
                        "description": "Number of shares to trade (1-10,000). Must be a whole number. Total cost = price × amount for buy orders.",
                        "domain": {
                            "type": "numeric_range",
                            "values": [1, 10000],
                            "importance": 0.8
                        },
                        "required": True
                    }
                ]
            },
            {
                "name": "make_transaction",
                "description": "Deposit money into or withdraw money from your trading account. Market must be open for transactions. This affects your available balance for trading.",
                "arguments": [
                    {
                        "name": "xact_type",
                        "description": "Transaction type. 'deposit' to add money to account, 'withdrawal' to remove money from account. Account must have sufficient balance for withdrawals.",
                        "domain": {
                            "type": "finite",
                            "values": ["deposit", "withdrawal"],
                            "importance": 0.9
                        },
                        "required": True
                    },
                    {
                        "name": "amount",
                        "description": "Amount in USD to deposit or withdraw (0.01-1,000,000). Must be positive. For withdrawals, cannot exceed current account balance.",
                        "domain": {
                            "type": "numeric_range",
                            "values": [0.01, 1000000.0],
                            "importance": 0.9
                        },
                        "required": True
                    }
                ]
            },
            {
                "name": "get_account_info",
                "description": "Get information about your trading account including account ID, current balance, and associated payment card. Use this to check available funds before trading.",
                "arguments": []
            },
            {
                "name": "fund_account",
                "description": "Add funds to your trading account from an external source. Similar to make_transaction with deposit, but specifically for account funding operations.",
                "arguments": [
                    {
                        "name": "amount",
                        "description": "Amount in USD to add to the account (0.01-1,000,000). Must be positive. This increases your available trading balance.",
                        "domain": {
                            "type": "numeric_range",
                            "values": [0.01, 1000000.0],
                            "importance": 0.9
                        },
                        "required": True
                    }
                ]
            },
            {
                "name": "remove_stock_from_watchlist",
                "description": "Remove a stock from your personal watchlist. Stock must currently be in your watchlist. Use get_watchlist to see current watchlist contents.",
                "arguments": [
                    {
                        "name": "symbol",
                        "description": "Stock symbol to remove from watchlist. Must be a symbol currently in your watchlist. Check current watchlist with get_watchlist if unsure.",
                        "domain": {
                            "type": "string",
                            "importance": 0.9,
                            "data_dependent": True
                        },
                        "required": True
                    }
                ]
            },
            {
                "name": "get_watchlist",
                "description": "Get your current stock watchlist showing all symbols you're tracking. Use this to see which stocks you're monitoring before adding or removing items.",
                "arguments": []
            },
            {
                "name": "get_order_history",
                "description": "Get a list of all your order IDs in chronological order. Returns just the order IDs - use get_order_details with specific IDs to get detailed information.",
                "arguments": []
            },
            {
                "name": "get_transaction_history",
                "description": "Get your account transaction history within a date range. Shows deposits, withdrawals, and their timestamps. Useful for account reconciliation and record keeping.",
                "arguments": [
                    {
                        "name": "start_date",
                        "description": "Optional start date for history filter in YYYY-MM-DD format (e.g., '2024-01-15'). If omitted, returns all transactions from the beginning. Must use hyphens as separators.",
                        "domain": {
                            "type": "string",
                            "importance": 0.7
                        },
                        "required": False,
                        "default": None
                    },
                    {
                        "name": "end_date",
                        "description": "Optional end date for history filter in YYYY-MM-DD format (e.g., '2024-12-31'). If omitted, returns transactions up to present. Must use hyphens as separators.",
                        "domain": {
                            "type": "string",
                            "importance": 0.7
                        },
                        "required": False,
                        "default": None
                    }
                ]
            },
            {
                "name": "update_stock_price",
                "description": "Update the current price of a stock in the system. This is an administrative function that changes the market price and recalculates percentage change.",
                "arguments": [
                    {
                        "name": "symbol",
                        "description": "Stock symbol to update price for. Must be a valid symbol in the trading system. Use get_stock_info to verify symbol exists.",
                        "domain": {
                            "type": "string",
                            "importance": 0.9,
                            "data_dependent": True
                        },
                        "required": True
                    },
                    {
                        "name": "new_price",
                        "description": "New price for the stock in USD (0.01-10,000). Must be positive. This becomes the new market price and affects percentage change calculations.",
                        "domain": {
                            "type": "numeric_range",
                            "values": [0.01, 10000.0],
                            "importance": 0.9
                        },
                        "required": True
                    }
                ]
            },
            {
                "name": "get_available_stocks",
                "description": "Get a list of stock symbols available in a specific sector. Useful for discovering investment opportunities within particular industries.",
                "arguments": [
                    {
                        "name": "sector",
                        "description": "Industry sector to get stocks from. Available sectors: 'Technology' (tech companies), 'Automobile' (car manufacturers), 'Healthcare' (medical companies), 'Finance' (financial services), 'Energy' (energy companies).",
                        "domain": {
                            "type": "finite",
                            "values": ["Technology", "Automobile", "Healthcare", "Finance", "Energy"],
                            "importance": 0.8
                        },
                        "required": True
                    }
                ]
            },
            {
                "name": "filter_stocks_by_price",
                "description": "Filter a list of stocks to only show those within a specific price range. IMPORTANT: The 'stocks' parameter must be a LIST of stock symbols, even for a single stock.",
                "arguments": [
                    {
                        "name": "stocks",
                        "description": "LIST of stock symbols to filter. MUST BE A LIST FORMAT: ['AAPL'] for one stock, ['AAPL', 'GOOG', 'TSLA'] for multiple stocks. Use get_available_stocks to get sector lists or provide your own list.",
                        "domain": {
                            "type": "list",
                            "importance": 0.9
                        },
                        "required": True
                    },
                    {
                        "name": "min_price",
                        "description": "Minimum stock price in USD (0.01-10,000). Only stocks with prices at or above this value will be included in results.",
                        "domain": {
                            "type": "numeric_range",
                            "values": [0.01, 10000.0],
                            "importance": 0.8
                        },
                        "required": True
                    },
                    {
                        "name": "max_price",
                        "description": "Maximum stock price in USD (0.01-10,000). Only stocks with prices at or below this value will be included. Must be greater than or equal to min_price.",
                        "domain": {
                            "type": "numeric_range",
                            "values": [0.01, 10000.0],
                            "importance": 0.8
                        },
                        "required": True
                    }
                ]
            },
            {
                "name": "add_to_watchlist",
                "description": "Add a stock to your personal watchlist for monitoring. Stock symbol must be valid and available in the trading system.",
                "arguments": [
                    {
                        "name": "stock",
                        "description": "Stock symbol to add to watchlist (e.g., 'AAPL', 'GOOG'). Must be a valid symbol in the system. Use get_stock_info to verify symbol exists before adding.",
                        "domain": {
                            "type": "string",
                            "importance": 0.9,
                            "data_dependent": True
                        },
                        "required": True
                    }
                ]
            },
            {
                "name": "notify_price_change",
                "description": "Check if any stocks in a list have significant price changes above a threshold. IMPORTANT: The 'stocks' parameter must be a LIST of stock symbols.",
                "arguments": [
                    {
                        "name": "stocks",
                        "description": "LIST of stock symbols to monitor for price changes. MUST BE A LIST FORMAT: ['AAPL'] for one stock, ['AAPL', 'GOOG', 'TSLA'] for multiple stocks. Each symbol must be valid in the system.",
                        "domain": {
                            "type": "list",
                            "importance": 0.9
                        },
                        "required": True
                    },
                    {
                        "name": "threshold",
                        "description": "Percentage change threshold to trigger notification (0.01-100.0). For example, 5.0 means notify if any stock changed by 5% or more (up or down).",
                        "domain": {
                            "type": "numeric_range",
                            "values": [0.01, 100.0],
                            "importance": 0.8
                        },
                        "required": True
                    }
                ]
            }
        ]
    

    def get_tools(self) -> List[Dict[str, Any]]:
        """Get the list of tools provided by this plugin."""
        return self._tools
    
    def _invalidate_domain_cache(self):
        """Invalidate the domain cache when trading system state changes."""
        self._domain_cache = None
    
    def _update_dynamic_domains(self) -> Dict[str, Any]:
        """Update domains based on current trading system state."""
        if self._domain_cache is not None:
            return self._domain_cache
        
        try:
            updates = {}
            
            # Update stock symbol domains
            stock_symbols = list(self.trading_bot.stocks.keys())
            if stock_symbols:
                # Update all tools that use stock symbols
                stock_symbol_fields = [
                    "get_stock_info.symbol",
                    "place_order.symbol", 
                    "remove_stock_from_watchlist.symbol",
                    "update_stock_price.symbol",
                    "add_to_watchlist.stock"
                ]
                for field in stock_symbol_fields:
                    updates[field] = {
                        "type": "finite",
                        "values": stock_symbols
                    }
            
            # Update watchlist domains - only stocks currently in watchlist can be removed
            watchlist = self.trading_bot.watch_list
            if watchlist:
                updates["remove_stock_from_watchlist.symbol"] = {
                    "type": "finite",
                    "values": watchlist
                }
            
            # Update order ID domains
            order_ids = list(self.trading_bot.orders.keys())
            if order_ids:
                for tool_name in ["get_order_details", "cancel_order"]:
                    updates[f"{tool_name}.order_id"] = {
                        "type": "finite",
                        "values": order_ids
                    }
            
            # Cache the result
            self._domain_cache = updates
            return updates
            
        except Exception as e:
            logger.error(f"Error updating dynamic domains: {e}")
            return {}
    
    def initialize_from_config(self, config_data: Dict[str, Any]) -> bool:
        """Initialize the trading bot from configuration data."""
        if "TradingBot" in config_data:
            trading_config = config_data["TradingBot"]
            self.trading_bot._load_scenario(trading_config)
            self._invalidate_domain_cache()  # Invalidate cache after loading
            return True
        return False
    
    def execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool with the given parameters."""
        # Cast parameters first using the base class method
        casted_params, cast_error = self._cast_parameters(tool_name, parameters)
        if cast_error:
            return {
                "success": False,
                "message": f"Parameter casting error: {cast_error}",
                "error": "TYPE_CASTING_ERROR"
            }
        
        # Validate parameters
        is_valid, error = self.validate_tool_call(tool_name, casted_params)
        if not is_valid:
            return {
                "success": False,
                "message": error,
                "error": "INVALID_PARAMETERS"
            }
        
        try:
            # Call the corresponding method on the trading bot
            if hasattr(self.trading_bot, tool_name):
                bot_method = getattr(self.trading_bot, tool_name)
                result = bot_method(**casted_params)
                
                # Invalidate domain cache if this was a state-changing operation
                if tool_name in self._state_changing_operations:
                    self._invalidate_domain_cache()
                
                # Check if the result indicates an error
                if isinstance(result, dict) and "error" in result:
                    return {
                        "success": False,
                        "message": result["error"],
                        "error": "OPERATION_FAILED"
                    }
                else:
                    return {
                        "success": True,
                        "message": f"Successfully executed {tool_name}",
                        "output": result
                    }
            else:
                return {
                    "success": False,
                    "message": f"Unknown tool: {tool_name}",
                    "error": "UNKNOWN_TOOL"
                }
        except Exception as e:
            logger.exception(f"Error executing {tool_name}: {e}")
            return {
                "success": False,
                "message": str(e),
                "error": "EXECUTION_ERROR"
            }
    
    def validate_tool_call(self, tool_name: str, parameters: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """Validate a tool call before execution."""
        # Find the tool definition
        tool_def = None
        for tool in self._tools:
            if tool["name"] == tool_name:
                tool_def = tool
                break
        
        if not tool_def:
            return False, f"Unknown tool: {tool_name}"
        
        # Check required arguments
        for arg_def in tool_def.get("arguments", []):
            if arg_def.get("required", True) and arg_def["name"] not in parameters:
                return False, f"Missing required argument: {arg_def['name']}"
            
            # If the argument is provided, validate its value
            if arg_def["name"] in parameters and parameters[arg_def["name"]] != "<UNK>":
                value = parameters[arg_def["name"]]
                
                # Skip empty values for optional parameters
                if value is None and not arg_def.get("required", True):
                    continue
                    
                # Validate based on domain type
                domain = arg_def.get("domain", {})
                domain_type = domain.get("type", "string")
                
                if domain_type == "numeric_range":
                    try:
                        val = float(value)
                        start, end = domain.get("values", [0, 1000000])
                        if not (start <= val <= end):
                            return False, f"Value {value} for {arg_def['name']} is out of range [{start}, {end}]"
                    except (ValueError, TypeError):
                        return False, f"Invalid numeric value for {arg_def['name']}: {value}"
                
                elif domain_type == "finite":
                    # Get dynamic domain values if data_dependent
                    if domain.get("data_dependent"):
                        dynamic_domains = self._update_dynamic_domains()
                        domain_key = f"{tool_name}.{arg_def['name']}"
                        if domain_key in dynamic_domains:
                            valid_values = dynamic_domains[domain_key].get("values", [])
                        else:
                            valid_values = domain.get("values", [])
                    else:
                        valid_values = domain.get("values", [])
                    
                    if value not in valid_values:
                        values_str = ", ".join(str(v) for v in valid_values)
                        return False, f"Invalid value for {arg_def['name']}: {value}. Expected one of: {values_str}"
                
                elif domain_type == "boolean":
                    if not isinstance(value, bool) and value not in [True, False, "true", "false", "True", "False"]:
                        return False, f"Invalid boolean value for {arg_def['name']}: {value}"
                
                elif domain_type == "list":
                    if not isinstance(value, list):
                        return False, f"Invalid list value for {arg_def['name']}: {value}"
        
        return True, None
    
    def get_domain_updates_from_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Update tool domains based on context."""
        # Initialize from config if available
        if "initial_config" in context:
            self.initialize_from_config(context["initial_config"])
        
        # Return dynamic domain updates
        return self._update_dynamic_domains()
    
    def get_uncertainty_context(self) -> Dict[str, Any]:
        """Get trading-specific context for uncertainty calculation."""
        try:
            context = {
                "has_orders": len(self.trading_bot.orders) > 0,
                "has_watchlist": len(self.trading_bot.watch_list) > 0,
                "market_status": self.trading_bot.market_status,
                "account_balance": self.trading_bot.account_info.get("balance", 0)
            }
            
            if context["has_orders"]:
                    
                context["available_order_ids"] = list(self.trading_bot.orders.keys())
                # Add order status information for validation checking
                context["order_statuses"] = {
                    order_id: order_info.get("status", "Unknown") for order_id, order_info in self.trading_bot.orders.items() if isinstance(order_info, dict)
                }

                
                
            
            if context["has_watchlist"]:
                context["watchlist_symbols"] = self.trading_bot.watch_list
            
            # Add available stock symbols
            context["available_stocks"] = list(self.trading_bot.stocks.keys())
            
            return context
        except Exception as e:
            logger.error(f"Error getting uncertainty context: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")  # Add this line
            return {}
    
    def get_prompt_templates(self) -> Dict[str, str]:
        """Get trading-specific prompt templates."""
        return {
            "tool_selection": """
You are an AI assistant that helps users with stock trading operations.

Conversation history:
{conversation_history}

User query: "{user_query}"

Available tools:
{tool_descriptions}

Please analyze the user's query and determine which tool(s) should be called to fulfill the request.
For each tool, specify all required parameters. If a parameter is uncertain, use "<UNK>" as the value.

Think through this step by step:
1. What is the user trying to do with the trading system?
2. Which trading operation(s) are needed to complete this task?
3. What parameters are needed for each operation?
4. Which parameters can be determined from the query, and which are uncertain?

Consider trading-specific constraints:
- Market must be open for certain operations (transactions, deposits/withdrawals)
- Order IDs must exist to cancel or get details
- Stock symbols must be valid for trading operations
- Account balance affects ability to make purchases or withdrawals

Return your response as a JSON object with the following structure:
{
  "reasoning": "Your step-by-step reasoning about what tools to use and why",
  "tool_calls": [
    {
      "tool_name": "name_of_tool",
      "arguments": {
        "arg1": "value1",
        "arg2": "<UNK>"
      }
    }
  ]
}
""",
            "question_generation": """
You are an AI assistant that helps users with stock trading operations.

Conversation history:
{conversation_history}

Original user query: "{user_query}"

I've determined that the following tool calls are needed, but some arguments are uncertain:

Tool Calls:
{tool_calls}

Uncertain Arguments:
{uncertain_args}

Your task is to generate clarification questions that would help resolve the uncertainty about specific arguments.

Consider the context of trading operations:
- Stock symbols (AAPL, GOOG, TSLA, etc.)
- Order types (Buy, Sell)
- Price ranges and amounts
- Account balance considerations
- Market timing

Instructions:
1. Generate questions that are clear, specific, and directly address the uncertain arguments
2. Each question should target one or more specific arguments
3. Questions should be conversational and easy for a user to understand
4. For each question, specify which tool and argument(s) it aims to clarify

Return your response as a JSON object with the following structure:
{
  "questions": [
    {
      "question": "A clear question to ask the user about trading operations",
      "target_args": [["tool_name", "arg_name"], ["tool_name", "other_arg_name"]]
    }
  ]
}
"""
        }