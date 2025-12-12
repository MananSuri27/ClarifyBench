from typing import Dict, List, Any, Optional, Tuple, Union
import logging
from datetime import datetime
from plugins.base_plugin import BasePlugin

logger = logging.getLogger(__name__)

class TravelAPI:
    """Travel API for handling flight bookings, credit cards, and related operations."""
    
    def __init__(self):
        """Initialize the Travel API with default values."""
        self.credit_card_list = {}
        self.booking_record = {}
        self.user_first_name = None
        self.user_last_name = None
        self.budget_limit = None
        self._api_description = "This tool belongs to the travel system, which allows users to book flights, manage credit cards, and view budget information."
        self._random = None  # Will be initialized later
        
        # Define base costs for available routes
        self.base_costs = {
            ("SFO", "LAX"): 200,
            ("SFO", "JFK"): 500,
            ("SFO", "ORD"): 400,
            ("SFO", "BOS"): 450,
            ("SFO", "RMS"): 300,
            ("SFO", "SBK"): 350,
            ("SFO", "MPC"): 370,
            ("SFO", "SVP"): 320,
            ("SFO", "SHD"): 330,
            ("SFO", "SSV"): 340,
            ("SFO", "OKD"): 360,
            ("SFO", "WLB"): 310,
            ("SFO", "CRH"): 380,
            ("SFO", "ATV"): 390,
            ("SFO", "PHV"): 420,
            ("SFO", "GFD"): 430,
            ("SFO", "CIA"): 700,
            ("LAX", "SFO"): 100,
            ("LAX", "JFK"): 600,
            ("LAX", "ORD"): 500,
            ("LAX", "BOS"): 550,
            ("LAX", "RMS"): 310,
            ("LAX", "SBK"): 320,
            ("LAX", "MPC"): 330,
            ("LAX", "SVP"): 340,
            ("LAX", "SHD"): 350,
            ("LAX", "SSV"): 360,
            ("LAX", "OKD"): 370,
            ("LAX", "WLB"): 380,
            ("LAX", "CRH"): 390,
            ("LAX", "ATV"): 400,
            ("LAX", "PHV"): 410,
            ("LAX", "GFD"): 420,
            ("LAX", "HND"): 430,
            ("JFK", "ORD"): 300,
            ("JFK", "BOS"): 250,
            ("JFK", "RMS"): 450,
            ("JFK", "SBK"): 460,
            ("JFK", "MPC"): 470,
            ("JFK", "SVP"): 480,
            ("JFK", "SHD"): 490,
            ("JFK", "SSV"): 500,
            ("JFK", "OKD"): 510,
            ("JFK", "WLB"): 520,
            ("JFK", "CRH"): 530,
            ("JFK", "ATV"): 540,
            ("JFK", "PHV"): 550,
            ("JFK", "GFD"): 560,
            ("JFK", "LAX"): 570,
            ("JFK", "HND"): 800,
            ("JFK", "PVG"): 950,
            ("JFK", "PEK"): 1000,
            ("ORD", "LAX"): 180,
            ("ORD", "BOS"): 200,
            ("ORD", "RMS"): 350,
            ("ORD", "SBK"): 360,
            ("ORD", "MPC"): 370,
            ("ORD", "SVP"): 380,
            ("ORD", "SHD"): 390,
            ("ORD", "SSV"): 400,
            ("ORD", "OKD"): 410,
            ("ORD", "WLB"): 420,
            ("ORD", "CRH"): 430,
            ("ORD", "ATV"): 440,
            ("ORD", "PHV"): 450,
            ("ORD", "GFD"): 460,
            ("BOS", "RMS"): 400,
            ("BOS", "SBK"): 410,
            ("BOS", "MPC"): 420,
            ("BOS", "SVP"): 430,
            ("BOS", "SHD"): 440,
            ("BOS", "SSV"): 450,
            ("BOS", "OKD"): 460,
            ("BOS", "WLB"): 470,
            ("BOS", "CRH"): 480,
            ("BOS", "ATV"): 490,
            ("BOS", "PHV"): 500,
            ("BOS", "GFD"): 510,
            ("RMS", "BOS"): 200,
            ("RMS", "JFK"): 210,
            ("RMS", "SBK"): 220,
            ("RMS", "MPC"): 230,
            ("RMS", "SVP"): 240,
            ("RMS", "SHD"): 250,
            ("RMS", "SSV"): 260,
            ("RMS", "OKD"): 270,
            ("RMS", "WLB"): 280,
            ("RMS", "CRH"): 290,
            ("RMS", "ATV"): 300,
            ("RMS", "PHV"): 310,
            ("RMS", "GFD"): 320,
            ("RMS", "LAX"): 330,
            ("SBK", "MPC"): 200,
            ("SBK", "SVP"): 210,
            ("SBK", "SHD"): 220,
            ("SBK", "SSV"): 230,
            ("SBK", "OKD"): 240,
            ("SBK", "WLB"): 250,
            ("SBK", "CRH"): 260,
            ("SBK", "ATV"): 270,
            ("SBK", "PHV"): 280,
            ("SBK", "GFD"): 290,
            ("MPC", "SVP"): 210,
            ("MPC", "SHD"): 220,
            ("MPC", "SSV"): 230,
            ("MPC", "OKD"): 240,
            ("MPC", "WLB"): 250,
            ("MPC", "CRH"): 260,
            ("MPC", "ATV"): 270,
            ("MPC", "PHV"): 280,
            ("MPC", "GFD"): 290,
            ("SVP", "SHD"): 230,
            ("SVP", "SSV"): 240,
            ("SVP", "OKD"): 250,
            ("SVP", "WLB"): 260,
            ("SVP", "CRH"): 270,
            ("SVP", "ATV"): 280,
            ("SVP", "PHV"): 290,
            ("SVP", "GFD"): 300,
            ("SHD", "SSV"): 220,
            ("SHD", "OKD"): 230,
            ("SHD", "WLB"): 240,
            ("SHD", "CRH"): 250,
            ("SHD", "ATV"): 260,
            ("SHD", "PHV"): 270,
            ("SHD", "GFD"): 280,
            ("SSV", "OKD"): 240,
            ("SSV", "WLB"): 250,
            ("SSV", "CRH"): 260,
            ("SSV", "ATV"): 270,
            ("SSV", "PHV"): 280,
            ("SSV", "GFD"): 290,
            ("OKD", "WLB"): 230,
            ("OKD", "CRH"): 240,
            ("OKD", "ATV"): 250,
            ("OKD", "PHV"): 260,
            ("OKD", "GFD"): 270,
            ("WLB", "CRH"): 250,
            ("WLB", "ATV"): 260,
            ("WLB", "PHV"): 270,
            ("WLB", "GFD"): 280,
            ("CRH", "ATV"): 240,
            ("CRH", "PHV"): 250,
            ("CRH", "GFD"): 260,
            ("CRH", "SFO"): 270,
            ("CRH", "RMS"): 280,
            ("CRH", "HKG"): 290,
            ("CRH", "JFK"): 300,
            ("ATV", "PHV"): 230,
            ("ATV", "GFD"): 240,
            ("PHV", "GFD"): 220,
            ("LHR", "CDG"): 100,
            ("OKD", "LAX"): 220
        }
    
    def _load_scenario(self, scenario: Dict[str, Any]):
        """
        Load a scenario with predefined data.
        
        Args:
            scenario: Dictionary containing scenario data
        """
        import random
        
        self._random = random.Random(scenario.get("random_seed", 141053))
        self.credit_card_list = scenario.get("credit_card_list", {})
        self.booking_record = scenario.get("booking_record", {})
        self.user_first_name = scenario.get("user_first_name", None)
        self.user_last_name = scenario.get("user_last_name", None)
        self.budget_limit = scenario.get("budget_limit", None)
        
        # Update base_costs if provided in scenario
        if "base_costs" in scenario:
            self.base_costs.update(scenario["base_costs"])
    
    def get_budget_fiscal_year(
        self,
        lastModifiedAfter: Optional[str] = None,
        includeRemoved: Optional[str] = None,
    ) -> Dict[str, str]:
        """
        Get the budget fiscal year

        Args:
            lastModifiedAfter: [Optional] Use this field if you only want Fiscal Years that were changed after the supplied date.
            includeRemoved: [Optional] If true, the service will return all Fiscal Years, including those that were previously removed.
        Returns:
            Dictionary containing the budget fiscal year
        """
        return {"budget_fiscal_year": "2018"}
    
    def get_flight_cost(
        self, travel_from: str, travel_to: str, travel_date: str, travel_class: str
    ) -> Dict[str, Union[List[float], str]]:
        """
        Get the list of cost of a flight in USD based on location, date, and class

        Args:
            travel_from: The 3 letter code of the departing airport
            travel_to: The 3 letter code of the arriving airport
            travel_date: The date of the travel in the format 'YYYY-MM-DD'
            travel_class: The class of the travel. Options are: economy, business, first.
        Returns:
            Dictionary containing a list of flight costs or error message
        """
        # Get the base cost, raise an error if the route is not available
        travel_pair = (travel_from, travel_to)
        if travel_pair in self.base_costs:
            base_cost = self.base_costs[travel_pair]
        else:
            return {"error": "No available route for the given airports."}

        # Determine the multiplier based on the travel class
        if travel_class == "economy":
            factor = 1
        elif travel_class == "business":
            factor = 2
        elif travel_class == "first":
            factor = 5
        else:
            return {"error": "Invalid travel class. Options are: economy, business, first."}

        # Determine the multiplier based on the travel date
        digit_sum = sum(int(char) for char in travel_date if char.isdigit())
        travel_date_multiplier = 2 if digit_sum % 2 == 0 else 1

        # Calculate the total cost
        travel_cost = float(base_cost * factor * travel_date_multiplier)
        return {"travel_cost_list": [travel_cost]}
    
    def list_all_airports(self) -> Dict[str, List[str]]:
        """
        List all available airports

        Returns:
            Dictionary containing a list of all available airports
        """
        # Get airports from base_costs and add additional airports
        airport_set = set()
        for route in self.base_costs.keys():
            airport_set.add(route[0])
            airport_set.add(route[1])
        
        # Add additional airports that might not be in routes
        additional_airports = [
            "RMS",
            "SBK",
            "MPC",
            "SVP",
            "SHD",
            "CDG",
            "LHR",
            "SSV",
            "OKD",
            "WLB",
            "PEK",
            "HND",
            "HKG",
            "CIA",
            "CRH",
            "ATV",
            "PHV",
            "GFD",
            "SFO",
            "LAX",
            "JFK",
            "ORD",
            "BOS",
        ]
        
        airport_set.update(additional_airports)
        airports = sorted(list(airport_set))
        return {"airports": airports}
    
    def compute_exchange_rate(
        self, base_currency: str, target_currency: str, value: float
    ) -> Dict[str, Union[float, str]]:
        """
        Compute the exchange rate between two currencies

        Args:
            base_currency: The base currency. [Enum]: USD, RMB, EUR, JPY, GBP, CAD, AUD, INR, RUB, BRL, MXN
            target_currency: The target currency. [Enum]: USD, RMB, EUR, JPY, GBP, CAD, AUD, INR, RUB, BRL, MXN
            value: The value to convert
        Returns:
            Dictionary containing the exchanged value or error message
        """
        exchange_rates = {
            ("USD", "RMB"): 7,
            ("USD", "EUR"): 0.8,
            ("USD", "JPY"): 110,
            ("USD", "GBP"): 0.7,
            ("USD", "CAD"): 1.3,
            ("USD", "AUD"): 1.4,
            ("USD", "INR"): 70,
            ("USD", "RUB"): 60,
            ("USD", "BRL"): 3.8,
            ("USD", "MXN"): 20
        }
        for key, val in exchange_rates.items():
            if base_currency == key[0] and target_currency == key[1]:
                return {"exchanged_value": value * val}
            elif base_currency == key[1] and target_currency == key[0]:
                return {"exchanged_value": round(value / val, 2)}
        return {"error": "No available exchange rate for the given currencies."}
    
    def verify_traveler_information(
        self, first_name: str, last_name: str, date_of_birth: str, passport_number: str
    ) -> Dict[str, Union[bool, str]]:
        """
        Verify the traveler information

        Args:
            first_name: The first name of the traveler
            last_name: The last name of the traveler
            date_of_birth: The date of birth of the traveler in the format YYYY-MM-DD
            passport_number: The passport number of the traveler
        Returns:
            Dictionary containing verification status or error message
        """
        if self.user_first_name != first_name or self.user_last_name != last_name:
            return {
                "verification_status": False,
                "verification_failure": "Cannot book flight information for another user."
                + f"Expected {self.user_first_name} {self.user_last_name}, got {first_name} {last_name}",
            }

        # Calculate age
        try:
            birth_date = datetime.strptime(date_of_birth, "%Y-%m-%d")
            today = datetime.today()
            age = (
                today.year
                - birth_date.year
                - ((today.month, today.day) < (birth_date.month, birth_date.day))
            )
        except ValueError:
            return {
                "verification_status": False,
                "verification_failure": "Invalid date of birth format. Please use YYYY-MM-DD.",
            }

        # Check if the traveler is at least 18 years old
        if age < 18:
            return {
                "verification_status": False,
                "verification_failure": "Traveler must be at least 18 years old.",
            }

        # Check if the passport number starts with 'US' (assuming this indicates a US passport)
        if not passport_number.startswith("US"):
            return {
                "verification_status": False,
                "verification_failure": "Passport must be issued by the United States.",
            }

        # If all checks pass
        return {"verification_status": True}
    
    def get_nearest_airport_by_city(self, location: str) -> Dict[str, str]:
        """
        Get the nearest airport to the given location

        Args:
            location: The name of the location. [Enum]: Rivermist, Stonebrook, Maplecrest, Silverpine, Shadowridge, London, Paris, Sunset Valley, Oakendale, Willowbend, Crescent Hollow, Autumnville, Pinehaven, Greenfield, San Francisco, Los Angeles, New York, Chicago, Boston, Beijing, Hong Kong, Rome, Tokyo
        Returns:
            Dictionary containing the nearest airport or error message
        """
        airport_map = {
            "Rivermist": "RMS",
            "Stonebrook": "SBK",
            "Maplecrest": "MPC",
            "Silverpine": "SVP",
            "Shadowridge": "SHD",
            "London": "LHR",
            "Paris": "CDG",
            "Sunset Valley": "SSV",
            "Oakendale": "OKD",
            "Willowbend": "WLB",
            "Crescent Hollow": "CRH",
            "Autumnville": "ATV",
            "Pinehaven": "PHV",
            "Greenfield": "GFD",
            "San Francisco": "SFO",
            "Los Angeles": "LAX",
            "New York": "JFK",
            "Chicago": "ORD",
            "Boston": "BOS",
            "Beijing": "PEK",
            "Hong Kong": "HKG",
            "Rome": "CIA",
            "Tokyo": "HND",
        }

        return {"nearest_airport": airport_map.get(location, "Unknown")}
    
    def register_credit_card(
        self,
        card_number: str,
        expiration_date: str,
        cardholder_name: str,
        card_verification_number: int,
    ) -> Dict[str, Union[str, Dict[str, str]]]:
        """
        Register a credit card

        Args:
            card_number: The credit card number
            expiration_date: The expiration date of the credit card in the format MM/YYYY
            cardholder_name: The name of the cardholder
            card_verification_number: The card verification number
        Returns:
            Dictionary containing the card_id or error message
        """
        import random
        if not self._random:
            self._random = random.Random(141053)
            
        if card_number in self.credit_card_list:
            return {"error": "Card already registered"}
        
        card_id = str(self._random.randint(100000000000, 999999999999))  # 12 digits
        self.credit_card_list[card_id] = {
            "card_number": card_number,
            "expiration_date": expiration_date,
            "cardholder_name": cardholder_name,
            "card_verification_number": card_verification_number,
            "balance": self._random.randint(10000, 99999),  # 5 digits
        }
        return {"card_id": card_id}
    
    def get_credit_card_balance(
        self, card_id: str
    ) -> Dict[str, Union[float, str]]:
        """
        Get the balance of a credit card
        
        Args:
            card_id: The ID of the credit card
        Returns:
            Dictionary containing the card balance or error message
        """
        if card_id not in self.credit_card_list:
            return {
                "error": "Card not registered. Here are a list of card_id's: "
                + str(list(self.credit_card_list.keys()))
            }
        return {"card_balance": self.credit_card_list[card_id]["balance"]}
    
    def book_flight(
        self,
        card_id: str,
        travel_date: str,
        travel_from: str,
        travel_to: str,
        travel_class: str,
        travel_cost: float,
    ) -> Dict[str, Union[str, bool]]:
        """
        Book a flight given the travel information. From and To should be the airport codes in the IATA format.

        Args:
            card_id: The ID of the credit card to use for the booking
            travel_date: The date of the travel in the format YYYY-MM-DD
            travel_from: The location the travel is from
            travel_to: The location the travel is to
            travel_class: The class of the travel
            travel_cost: The cost of the travel
        Returns:
            Dictionary containing booking information or error message
        """
        import random
        if not self._random:
            self._random = random.Random(141053)
            
        if card_id not in self.credit_card_list:
            return {"booking_status": False, "error": "Card not registered"}
        if "balance" not in self.credit_card_list[card_id]:
            return {"booking_status": False, "error": "Balance not found"}
        if self.credit_card_list[card_id]["balance"] < travel_cost:
            return {"booking_status": False, "error": "Insufficient funds"}
        if (
            self.budget_limit is not None
            and travel_cost > self.budget_limit
        ):
            return {
                "booking_status": False,
                "error": "Travel cost exceeds budget limit",
            }
        
        travel_cost = float(travel_cost)
        self.credit_card_list[card_id]["balance"] -= travel_cost
        booking_id = str(self._random.randint(1000000, 9999999))  # 7 digits
        transaction_id = str(self._random.randint(10000000, 99999999))  # 8 digits
        self.booking_record[booking_id] = {
            "card_id": card_id,
            "travel_date": travel_date,
            "travel_from": travel_from,
            "travel_to": travel_to,
            "travel_class": travel_class,
            "travel_cost": travel_cost,
            "transaction_id": transaction_id,
        }
        return {
            "booking_id": booking_id,
            "transaction_id": transaction_id,
            "booking_status": True,
        }
    
    def retrieve_invoice(
        self,
        booking_id: Optional[str] = None,
        insurance_id: Optional[str] = None,
    ) -> Dict[str, Union[Dict[str, Union[str, float]], str]]:
        """
        Retrieve the invoice for a booking

        Args:
            booking_id: [Optional] The ID of the booking
            insurance_id: [Optional] The ID of the insurance
        Returns:
            Dictionary containing invoice information or error message
        """
        if booking_id not in self.booking_record:
            return {"error": "Booking not found"}
        
        invoice = {
            "booking_id": booking_id,
            "travel_date": self.booking_record[booking_id]["travel_date"],
            "travel_from": self.booking_record[booking_id]["travel_from"],
            "travel_to": self.booking_record[booking_id]["travel_to"],
            "travel_class": self.booking_record[booking_id]["travel_class"],
            "travel_cost": self.booking_record[booking_id]["travel_cost"],
            "transaction_id": self.booking_record[booking_id]["transaction_id"],
        }
        return {"invoice": invoice}
    
    def cancel_booking(
        self, booking_id: str
    ) -> Dict[str, Union[bool, str]]:
        """
        Cancel a booking

        Args:
            booking_id: The ID of the booking
        Returns:
            Dictionary containing cancellation status or error message
        """
        if booking_id not in self.booking_record:
            return {"cancel_status": False, "error": "Booking not found"}
        
        card_id = self.booking_record[booking_id]["card_id"]
        travel_cost = self.booking_record[booking_id]["travel_cost"]
        self.credit_card_list[card_id]["balance"] += travel_cost
        del self.booking_record[booking_id]
        return {"cancel_status": True}
    
    def set_budget_limit(
        self, budget_limit: float
    ) -> Dict[str, Union[float, str]]:
        """
        Set the budget limit for the user

        Args:
            budget_limit: The budget limit to set in USD
        Returns:
            Dictionary containing the budget limit
        """
        budget_limit = float(budget_limit)
        self.budget_limit = budget_limit
        return {"budget_limit": budget_limit}
    
    def purchase_insurance(
        self,
        insurance_type: str,
        booking_id: str,
        insurance_cost: float,
        card_id: str,
    ) -> Dict[str, Union[str, bool]]:
        """
        Purchase insurance

        Args:
            insurance_type: The type of insurance to purchase
            insurance_cost: The cost of the insurance
            booking_id: The ID of the booking
            card_id: The ID of the credit card to use for the insurance purchase
        Returns:
            Dictionary containing insurance information or error message
        """
        import random
        if not self._random:
            self._random = random.Random(141053)
            
        if self.budget_limit is not None and insurance_cost > self.budget_limit:
            return {"insurance_status": False, "error": "Insurance cost exceeds budget limit"}
        if booking_id not in self.booking_record:
            return {"insurance_status": False, "error": "Booking not found"}
        if card_id not in self.credit_card_list:
            return {"insurance_status": False, "error": "Credit card not registered"}
        if self.credit_card_list[card_id]["balance"] < insurance_cost:
            return {"insurance_status": False, "error": "Insufficient funds"}
            
        self.credit_card_list[card_id]["balance"] -= insurance_cost
        return {
            "insurance_id": str(self._random.randint(100000000, 999999999)),  # 9 digits
            "insurance_status": True,
        }
    
    def contact_customer_support(self, booking_id: str, message: str) -> Dict[str, str]:
        """
        Contact travel booking customer support, get immediate support on an issue with an online call.

        Args:
            booking_id: The ID of the booking
            message: The message to send to customer support
        Returns:
            Dictionary containing the customer support message or error message
        """
        if booking_id not in self.booking_record:
            return {"error": "Booking not found"}
        return {
            "customer_support_message": "Thank you for contacting customer support. We will get back to you shortly. "
            + message
        }
    
    def get_all_credit_cards(self) -> Dict[str, Dict[str, Union[str, int, float]]]:
        """
        Get all registered credit cards

        Returns:
            Dictionary containing all registered credit cards
        """
        return {"credit_card_list": self.credit_card_list}

    def get_all_bookings(self) -> Dict[str, Union[Dict[str, Dict], str]]:
        """
        Get all flight bookings with detailed information

        Returns:
            Dictionary containing all bookings or error message
        """
        if not self.booking_record:
            return {"error": "No bookings found"}
        
        return {"all_bookings": self.booking_record}


class TravelPlugin(BasePlugin):
    """
    Plugin for travel-related operations.
    
    This plugin provides tools for booking flights, managing credit cards,
    and performing various travel-related operations with dynamic domain updates
    and proper type casting.
    """
    
    def __init__(self):
        """Initialize the travel plugin."""
        super().__init__()
        self.travel_api = TravelAPI()
        self._name = "travel"
        self._description = "Plugin for travel-related operations, including flight bookings, credit card management, and travel information."
        self._tools = self._generate_tool_definitions()
        
        # Cache for dynamic domains - invalidated when state changes
        self._domain_cache = None
        self._state_changing_operations = {
            'register_credit_card', 'book_flight', 'cancel_booking', 'set_budget_limit', 'purchase_insurance'
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
        """Generate tool definitions for the travel plugin."""
        return [
            {
                "name": "get_budget_fiscal_year",
                "description": "Get the budget fiscal year",
                "arguments": [
                    {
                        "name": "lastModifiedAfter",
                        "description": "Use this field if you only want Fiscal Years that were changed after the supplied date",
                        "domain": {
                            "type": "string",
                            "importance": 0.5
                        },
                        "required": False,
                        "default": None
                    },
                    {
                        "name": "includeRemoved",
                        "description": "If true, the service will return all Fiscal Years, including those that were previously removed",
                        "domain": {
                            "type": "string",
                            "importance": 0.5
                        },
                        "required": False,
                        "default": None
                    }
                ]
            },
            {
                "name": "register_credit_card",
                "description": "Register a credit card",
                "arguments": [
                    {
                        "name": "card_number",
                        "description": "The credit card number",
                        "domain": {
                            "type": "string",
                            "importance": 0.9
                        },
                        "required": True
                    },
                    {
                        "name": "expiration_date",
                        "description": "The expiration date of the credit card in the format MM/YYYY",
                        "domain": {
                            "type": "string",
                            "importance": 0.8
                        },
                        "required": True
                    },
                    {
                        "name": "cardholder_name",
                        "description": "The name of the cardholder",
                        "domain": {
                            "type": "string",
                            "importance": 0.8
                        },
                        "required": True
                    },
                    {
                        "name": "card_verification_number",
                        "description": "The card verification number",
                        "domain": {
                            "type": "numeric_range",
                            "values": [100, 999],
                            "importance": 0.8
                        },
                        "required": True
                    }
                ]
            },
            {
                "name": "get_flight_cost",
                "description": "Get the list of cost of a flight in USD based on location, date, and class",
                "arguments": [
                    {
                        "name": "travel_from",
                        "description": "The 3 letter code of the departing airport",
                        "domain": {
                            "type": "string",
                            "importance": 0.9,
                            "data_dependent": True
                        },
                        "required": True
                    },
                    {
                        "name": "travel_to",
                        "description": "The 3 letter code of the arriving airport",
                        "domain": {
                            "type": "string",
                            "importance": 0.9,
                            "data_dependent": True
                        },
                        "required": True
                    },
                    {
                        "name": "travel_date",
                        "description": "The date of the travel in the format 'YYYY-MM-DD'",
                        "domain": {
                            "type": "string",
                            "importance": 0.9
                        },
                        "required": True
                    },
                    {
                        "name": "travel_class",
                        "description": "The class of the travel. Options are: economy, business, first",
                        "domain": {
                            "type": "finite",
                            "values": ["economy", "business", "first"],
                            "importance": 0.8
                        },
                        "required": True
                    }
                ]
            },
            {
                "name": "get_credit_card_balance",
                "description": "Get the balance of a credit card",
                "arguments": [
                    {
                        "name": "card_id",
                        "description": "The ID of the credit card",
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
                "name": "book_flight",
                "description": "Book a flight given the travel information",
                "arguments": [
                    {
                        "name": "card_id",
                        "description": "The ID of the credit card to use for the booking",
                        "domain": {
                            "type": "string",
                            "importance": 0.9,
                            "data_dependent": True
                        },
                        "required": True
                    },
                    {
                        "name": "travel_date",
                        "description": "The date of the travel in the format YYYY-MM-DD",
                        "domain": {
                            "type": "string",
                            "importance": 0.9
                        },
                        "required": True
                    },
                    {
                        "name": "travel_from",
                        "description": "The location the travel is from (3-letter airport code)",
                        "domain": {
                            "type": "string",
                            "importance": 0.9,
                            "data_dependent": True
                        },
                        "required": True
                    },
                    {
                        "name": "travel_to",
                        "description": "The location the travel is to (3-letter airport code)",
                        "domain": {
                            "type": "string",
                            "importance": 0.9,
                            "data_dependent": True
                        },
                        "required": True
                    },
                    {
                        "name": "travel_class",
                        "description": "The class of the travel",
                        "domain": {
                            "type": "finite",
                            "values": ["economy", "business", "first"],
                            "importance": 0.8
                        },
                        "required": True
                    },
                    {
                        "name": "travel_cost",
                        "description": "The cost of the travel",
                        "domain": {
                            "type": "numeric_range",
                            "values": [0, 10000],
                            "importance": 0.9
                        },
                        "required": True
                    }
                ]
            },
            {
                "name": "retrieve_invoice",
                "description": "Retrieve the invoice for a booking",
                "arguments": [
                    {
                        "name": "booking_id",
                        "description": "The ID of the booking",
                        "domain": {
                            "type": "string",
                            "importance": 0.9,
                            "data_dependent": True
                        },
                        "required": False,
                        "default": None
                    },
                    {
                        "name": "insurance_id",
                        "description": "The ID of the insurance",
                        "domain": {
                            "type": "string",
                            "importance": 0.7,
                            "data_dependent": True
                        },
                        "required": False,
                        "default": None
                    }
                ]
            },
            {
                "name": "list_all_airports",
                "description": "List all available airports",
                "arguments": []
            },
            {
                "name": "cancel_booking",
                "description": "Cancel a booking",
                "arguments": [
                    {
                        "name": "booking_id",
                        "description": "The ID of the booking",
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
                "name": "compute_exchange_rate",
                "description": "Compute the exchange rate between two currencies",
                "arguments": [
                    {
                        "name": "base_currency",
                        "description": "The base currency",
                        "domain": {
                            "type": "finite",
                            "values": ["USD", "RMB", "EUR", "JPY", "GBP", "CAD", "AUD", "INR", "RUB", "BRL", "MXN"],
                            "importance": 0.9
                        },
                        "required": True
                    },
                    {
                        "name": "target_currency",
                        "description": "The target currency",
                        "domain": {
                            "type": "finite",
                            "values": ["USD", "RMB", "EUR", "JPY", "GBP", "CAD", "AUD", "INR", "RUB", "BRL", "MXN"],
                            "importance": 0.9
                        },
                        "required": True
                    },
                    {
                        "name": "value",
                        "description": "The value to convert",
                        "domain": {
                            "type": "numeric_range",
                            "values": [0, 1000000],
                            "importance": 0.9
                        },
                        "required": True
                    }
                ]
            },
            {
                "name": "verify_traveler_information",
                "description": "Verify the traveler information",
                "arguments": [
                    {
                        "name": "first_name",
                        "description": "The first name of the traveler",
                        "domain": {
                            "type": "string",
                            "importance": 0.9
                        },
                        "required": True
                    },
                    {
                        "name": "last_name",
                        "description": "The last name of the traveler",
                        "domain": {
                            "type": "string",
                            "importance": 0.9
                        },
                        "required": True
                    },
                    {
                        "name": "date_of_birth",
                        "description": "The date of birth of the traveler in the format YYYY-MM-DD",
                        "domain": {
                            "type": "string",
                            "importance": 0.9
                        },
                        "required": True
                    },
                    {
                        "name": "passport_number",
                        "description": "The passport number of the traveler",
                        "domain": {
                            "type": "string",
                            "importance": 0.9
                        },
                        "required": True
                    }
                ]
            },
            {
                "name": "set_budget_limit",
                "description": "Set the budget limit for the user",
                "arguments": [
                    {
                        "name": "budget_limit",
                        "description": "The budget limit to set in USD",
                        "domain": {
                            "type": "numeric_range",
                            "values": [0, 10000],
                            "importance": 0.9
                        },
                        "required": True
                    }
                ]
            },
            {
                "name": "get_nearest_airport_by_city",
                "description": "Get the nearest airport to the given location",
                "arguments": [
                    {
                        "name": "location",
                        "description": "The name of the location",
                        "domain": {
                            "type": "finite",
                            "values": [
                                "Rivermist", "Stonebrook", "Maplecrest", "Silverpine", "Shadowridge", 
                                "London", "Paris", "Sunset Valley", "Oakendale", "Willowbend", 
                                "Crescent Hollow", "Autumnville", "Pinehaven", "Greenfield", 
                                "San Francisco", "Los Angeles", "New York", "Chicago", "Boston", 
                                "Beijing", "Hong Kong", "Rome", "Tokyo"
                            ],
                            "importance": 0.9
                        },
                        "required": True
                    }
                ]
            },
            {
                "name": "purchase_insurance",
                "description": "Purchase insurance for a booking",
                "arguments": [
                    {
                        "name": "insurance_type",
                        "description": "The type of insurance to purchase",
                        "domain": {
                            "type": "finite",
                            "values": ["basic", "premium", "deluxe"],
                            "importance": 0.8
                        },
                        "required": True
                    },
                    {
                        "name": "booking_id",
                        "description": "The ID of the booking",
                        "domain": {
                            "type": "string",
                            "importance": 0.9,
                            "data_dependent": True
                        },
                        "required": True
                    },
                    {
                        "name": "insurance_cost",
                        "description": "The cost of the insurance",
                        "domain": {
                            "type": "numeric_range",
                            "values": [0, 1000],
                            "importance": 0.9
                        },
                        "required": True
                    },
                    {
                        "name": "card_id",
                        "description": "The ID of the credit card to use for the insurance purchase",
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
                "name": "contact_customer_support",
                "description": "Contact travel booking customer support",
                "arguments": [
                    {
                        "name": "booking_id",
                        "description": "The ID of the booking",
                        "domain": {
                            "type": "string",
                            "importance": 0.9,
                            "data_dependent": True
                        },
                        "required": True
                    },
                    {
                        "name": "message",
                        "description": "The message to send to customer support",
                        "domain": {
                            "type": "string",
                            "importance": 0.9
                        },
                        "required": True
                    }
                ]
            },
            {
                "name": "get_all_credit_cards",
                "description": "Get all registered credit cards",
                "arguments": []
            },
            # NEW TOOL: get_all_bookings
            {
                "name": "get_all_bookings",
                "description": "Get all flight bookings with detailed information",
                "arguments": []
            }
        ]
    
    def get_tools(self) -> List[Dict[str, Any]]:
        """Get the list of tools provided by this plugin."""
        return self._tools
    
    def _invalidate_domain_cache(self):
        """Invalidate the domain cache when travel system state changes."""
        self._domain_cache = None
    
    def _update_dynamic_domains(self) -> Dict[str, Any]:
        """Update domains based on current travel system state."""
        if self._domain_cache is not None:
            return self._domain_cache
        
        try:
            updates = {}
            
            # Update card_id domains based on available credit cards
            card_ids = list(self.travel_api.credit_card_list.keys())
            if card_ids:
                card_id_fields = [
                    "get_credit_card_balance.card_id",
                    "book_flight.card_id",
                    "purchase_insurance.card_id"
                ]
                for field in card_id_fields:
                    updates[field] = {
                        "type": "finite",
                        "values": card_ids
                    }
            
            # Update booking_id domains based on available bookings
            booking_ids = list(self.travel_api.booking_record.keys())
            if booking_ids:
                booking_id_fields = [
                    "retrieve_invoice.booking_id",
                    "cancel_booking.booking_id",
                    "purchase_insurance.booking_id",
                    "contact_customer_support.booking_id"
                ]
                for field in booking_id_fields:
                    updates[field] = {
                        "type": "finite",
                        "values": booking_ids
                    }
            
            # Update airport domains based on available routes
            airports = set()
            for route in self.travel_api.base_costs.keys():
                airports.add(route[0])
                airports.add(route[1])
            
            # Add additional airports from list_all_airports
            all_airports_response = self.travel_api.list_all_airports()
            if "airports" in all_airports_response:
                airports.update(all_airports_response["airports"])
            
            airport_list = sorted(list(airports))
            if airport_list:
                airport_fields = [
                    "get_flight_cost.travel_from",
                    "get_flight_cost.travel_to",
                    "book_flight.travel_from",
                    "book_flight.travel_to"
                ]
                for field in airport_fields:
                    updates[field] = {
                        "type": "finite",
                        "values": airport_list
                    }
            
            # Cache the result
            self._domain_cache = updates
            return updates
            
        except Exception as e:
            logger.error(f"Error updating dynamic domains: {e}")
            return {}
    
    def initialize_from_config(self, config_data: Dict[str, Any]) -> bool:
        """Initialize the travel API from configuration data."""
        if "TravelAPI" in config_data:
            travel_config = config_data["TravelAPI"]
            self.travel_api._load_scenario(travel_config)
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
            # Call the corresponding method on the travel API
            if hasattr(self.travel_api, tool_name):
                api_method = getattr(self.travel_api, tool_name)
                result = api_method(**casted_params)
                
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
        
        return True, None
    
    def get_domain_updates_from_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Update tool domains based on context."""
        # Initialize from config if available
        if "initial_config" in context:
            self.initialize_from_config(context["initial_config"])
        
        # Return dynamic domain updates
        return self._update_dynamic_domains()
    
    def get_uncertainty_context(self) -> Dict[str, Any]:
        """Get travel-specific context for uncertainty calculation."""
        try:
            context = {
                "has_credit_cards": len(self.travel_api.credit_card_list) > 0,
                "has_bookings": len(self.travel_api.booking_record) > 0,
                "budget_limit": self.travel_api.budget_limit,
                "user_name": f"{self.travel_api.user_first_name} {self.travel_api.user_last_name}" if self.travel_api.user_first_name else None
            }
            
            if context["has_credit_cards"]:
                context["available_card_ids"] = list(self.travel_api.credit_card_list.keys())
                # Add balance information for financial constraint checking
                context["card_balances"] = {
                    card_id: card_info.get("balance", 0) 
                    for card_id, card_info in self.travel_api.credit_card_list.items()
                }
            
            if context["has_bookings"]:
                context["available_booking_ids"] = list(self.travel_api.booking_record.keys())
            
            # Add available routes for travel planning
            context["available_routes"] = list(self.travel_api.base_costs.keys())
            
            return context
        except Exception as e:
            logger.error(f"Error getting uncertainty context: {e}")
            return {}
    
    def get_prompt_templates(self) -> Dict[str, str]:
        """Get travel-specific prompt templates."""
        return {
            "tool_selection": """
You are an AI assistant that helps users with travel-related operations.

Conversation history:
{conversation_history}

User query: "{user_query}"

Available tools:
{tool_descriptions}

Please analyze the user's query and determine which tool(s) should be called to fulfill the request.
For each tool, specify all required parameters. If a parameter is uncertain, use "<UNK>" as the value.

Think through this step by step:
1. What is the user trying to do with the travel system?
2. Which travel operation(s) are needed to complete this task?
3. What parameters are needed for each operation?
4. Which parameters can be determined from the query, and which are uncertain?

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
You are an AI assistant that helps users with travel-related operations.

Conversation history:
{conversation_history}

Original user query: "{user_query}"

I've determined that the following tool calls are needed, but some arguments are uncertain:

Tool Calls:
{tool_calls}

Uncertain Arguments:
{uncertain_args}

Your task is to generate clarification questions that would help resolve the uncertainty about specific arguments.

Instructions:
1. Generate questions that are clear, specific, and directly address the uncertain arguments
2. Each question should target one or more specific arguments
3. Questions should be conversational and easy for a user to understand
4. For each question, specify which tool and argument(s) it aims to clarify

Return your response as a JSON object with the following structure:
{
  "questions": [
    {
      "question": "A clear question to ask the user",
      "target_args": [["tool_name", "arg_name"], ["tool_name", "other_arg_name"]]
    }
  ]
}
"""
        }