import random
from copy import deepcopy
from typing import Dict, List, Any, Optional, Tuple, Union
import logging

from plugins.base_plugin import BasePlugin

logger = logging.getLogger(__name__)

MAX_FUEL_LEVEL = 50
MIN_FUEL_LEVEL = 0.0
MILE_PER_GALLON = 20.0
MAX_BATTERY_VOLTAGE = 14.0
MIN_BATTERY_VOLTAGE = 10.0

DEFAULT_STATE = {
    "random_seed": 141053,
    "fuelLevel": 0.0,
    "batteryVoltage": 12.6,
    "engine_state": "stopped",
    "remainingUnlockedDoors": 4,
    "doorStatus": {
        "driver": "unlocked",
        "passenger": "unlocked",
        "rear_left": "unlocked",
        "rear_right": "unlocked",
    },
    "acTemperature": 25.0,
    "fanSpeed": 50,
    "acMode": "auto",
    "humidityLevel": 50.0,
    "headLightStatus": "off",
    "parkingBrakeStatus": "released",
    "_parkingBrakeForce": 0.0,
    "_slopeAngle": 0.0,
    "brakePedalStatus": "released",
    "brakePedalForce": 0.0,
    "distanceToNextVehicle": 50.0,
    "cruiseStatus": "inactive",
    "destination": "None",
    "frontLeftTirePressure": 32.0,
    "frontRightTirePressure": 32.0,
    "rearLeftTirePressure": 30.0,
    "rearRightTirePressure": 30.0,
}


class VehicleControlAPI:
    """
    Vehicle control API for managing various aspects of a car including engine,
    doors, climate control, lights, brakes, and more.
    """

    def __init__(self):
        """Initialize the vehicle control API with default values."""
        self.fuelLevel: float
        self.batteryVoltage: float
        self.engine_state: str
        self.remainingUnlockedDoors: int
        self.doorStatus: Dict[str, str]
        self.acTemperature: float
        self.fanSpeed: int
        self.acMode: str
        self.humidityLevel: float
        self.headLightStatus: str
        self.parkingBrakeStatus: str
        self._parkingBrakeForce: float
        self._slopeAngle: float
        self.brakePedalStatus: str
        self._brakePedalForce: float
        self.distanceToNextVehicle: float
        self.cruiseStatus: str
        self.destination: str
        self.frontLeftTirePressure: float
        self.frontRightTirePressure: float
        self.rearLeftTirePressure: float
        self.rearRightTirePressure: float
        self._api_description = "Vehicle control system for managing car operations including engine, doors, climate, lights, and safety systems."

    def _load_scenario(self, scenario: dict) -> None:
        """Load scenario configuration for the vehicle control."""
        DEFAULT_STATE_COPY = deepcopy(DEFAULT_STATE)
        self._random = random.Random(
            scenario.get("random_seed", DEFAULT_STATE_COPY["random_seed"])
        )
        self.fuelLevel = scenario.get("fuelLevel", DEFAULT_STATE_COPY["fuelLevel"])
        self.batteryVoltage = scenario.get("batteryVoltage", DEFAULT_STATE_COPY["batteryVoltage"])
        self.engine_state = scenario.get("engineState", DEFAULT_STATE_COPY["engine_state"])
        self.remainingUnlockedDoors = scenario.get(
            "remainingUnlockedDoors", DEFAULT_STATE_COPY["remainingUnlockedDoors"]
        )
        self.doorStatus = scenario.get("doorStatus", DEFAULT_STATE_COPY["doorStatus"])
        self.remainingUnlockedDoors = 4 - len(
            [1 for door in self.doorStatus.keys() if self.doorStatus[door] == "locked"]
        )
        self.acTemperature = scenario.get("acTemperature", DEFAULT_STATE_COPY["acTemperature"])
        self.fanSpeed = scenario.get("fanSpeed", DEFAULT_STATE_COPY["fanSpeed"])
        self.acMode = scenario.get("acMode", DEFAULT_STATE_COPY["acMode"])
        self.humidityLevel = scenario.get("humidityLevel", DEFAULT_STATE_COPY["humidityLevel"])
        self.headLightStatus = scenario.get("headLightStatus", DEFAULT_STATE_COPY["headLightStatus"])
        self.parkingBrakeStatus = scenario.get(
            "parkingBrakeStatus", DEFAULT_STATE_COPY["parkingBrakeStatus"]
        )
        self._parkingBrakeForce = scenario.get(
            "parkingBrakeForce", DEFAULT_STATE_COPY["_parkingBrakeForce"]
        )
        self._slopeAngle = scenario.get("slopeAngle", DEFAULT_STATE_COPY["_slopeAngle"])
        self.brakePedalStatus = scenario.get("brakePedalStatus", DEFAULT_STATE_COPY["brakePedalStatus"])
        self._brakePedalForce = scenario.get("brakePedalForce", DEFAULT_STATE_COPY["brakePedalForce"])
        self.distanceToNextVehicle = scenario.get(
            "distanceToNextVehicle", DEFAULT_STATE_COPY["distanceToNextVehicle"]
        )
        self.cruiseStatus = scenario.get("cruiseStatus", DEFAULT_STATE_COPY["cruiseStatus"])
        self.destination = scenario.get("destination", DEFAULT_STATE_COPY["destination"])
        self.frontLeftTirePressure = scenario.get(
            "frontLeftTirePressure", DEFAULT_STATE_COPY["frontLeftTirePressure"]
        )
        self.frontRightTirePressure = scenario.get(
            "frontRightTirePressure", DEFAULT_STATE_COPY["frontRightTirePressure"]
        )
        self.rearLeftTirePressure = scenario.get(
            "rearLeftTirePressure", DEFAULT_STATE_COPY["rearLeftTirePressure"]
        )
        self.rearRightTirePressure = scenario.get(
            "rearRightTirePressure", DEFAULT_STATE_COPY["rearRightTirePressure"]
        )

    def __eq__(self, value: object) -> bool:
        """Compare two VehicleControlAPI instances for equality."""
        if not isinstance(value, VehicleControlAPI):
            return False

        for attr_name in vars(self):
            if attr_name.startswith("_"):
                continue
            model_attr = getattr(self, attr_name)
            ground_truth_attr = getattr(value, attr_name)

            if model_attr != ground_truth_attr:
                return False

        return True

    def startEngine(self, ignitionMode: str) -> Dict[str, Union[str, float]]:
        """
        Start or stop the engine of the vehicle.
        
        Args:
            ignitionMode (str): The ignition mode of the vehicle. [Enum]: ["START", "STOP"]
            
        Returns:
            engineState (str): The state of the engine. [Enum]: ["running", "stopped"]
            fuelLevel (float): The fuel level of the vehicle in gallons.
            batteryVoltage (float): The battery voltage of the vehicle in volts.
        """
        if ignitionMode == "STOP":
            self.engine_state = "stopped"
            return {
                "engineState": self.engine_state,
                "fuelLevel": self.fuelLevel,
                "batteryVoltage": self.batteryVoltage,
            }
        
        if self.remainingUnlockedDoors > 0:
            return {
                "error": "All doors must be locked before starting the engine. Here are the unlocked doors: "
                + ", ".join(
                    [
                        door
                        for door, status in self.doorStatus.items()
                        if status == "unlocked"
                    ]
                )
            }
        if self.brakePedalStatus != "pressed":
            return {"error": "Brake pedal needs to be pressed when starting the engine."}
        if self._brakePedalForce != 1000.0:
            return {"error": "Must press the brake fully before starting the engine."}
        if self.fuelLevel < MIN_FUEL_LEVEL:
            return {"error": "Fuel tank is empty."}
        if ignitionMode == "START":
            self.engine_state = "running"
        else:
            return {"error": "Invalid ignition mode."}

        return {
            "engineState": self.engine_state,
            "fuelLevel": self.fuelLevel,
            "batteryVoltage": self.batteryVoltage,
        }

    def fillFuelTank(self, fuelAmount: float) -> Dict[str, Union[str, float]]:
        """
        Fill the fuel tank of the vehicle. The fuel tank can hold up to 50 gallons.
        
        Args:
            fuelAmount (float): The amount of fuel to fill in gallons; additional fuel to add to the tank.
            
        Returns:
            fuelLevel (float): The fuel level of the vehicle in gallons.
        """
        if fuelAmount < 0:
            return {"error": "Fuel amount cannot be negative."}
        if self.fuelLevel + fuelAmount > MAX_FUEL_LEVEL:
            return {"error": "Cannot fill gas above the tank capacity."}
        if self.fuelLevel + fuelAmount < MIN_FUEL_LEVEL:
            return {"error": "Fuel tank is empty. Min fuel level is 0 gallons."}
        self.fuelLevel += fuelAmount
        return {"fuelLevel": self.fuelLevel}

    def lockDoors(self, unlock: bool, door: List[str]) -> Dict[str, Union[str, int]]:
        """
        Lock or unlock doors of the vehicle.
        
        Args:
            unlock (bool): True if the doors are to be unlocked, False otherwise.
            door (List[str]): The list of doors to lock or unlock. [Enum]: ["driver", "passenger", "rear_left", "rear_right"]
            
        Returns:
            lockStatus (str): The status of the lock. [Enum]: ["locked", "unlocked"]
            remainingUnlockedDoors (int): The number of remaining unlocked doors.
        """
        if unlock:
            for d in door:
                if self.doorStatus[d] == "unlocked":
                    continue
                self.doorStatus[d] = "unlocked"
                self.remainingUnlockedDoors += 1
            return {
                "lockStatus": "unlocked",
                "remainingUnlockedDoors": self.remainingUnlockedDoors,
            }
        else:
            for d in door:
                if self.doorStatus[d] == "locked":
                    continue
                self.doorStatus[d] = "locked"
                self.remainingUnlockedDoors -= 1
            return {
                "lockStatus": "locked",
                "remainingUnlockedDoors": self.remainingUnlockedDoors,
            }

    def adjustClimateControl(
        self,
        temperature: float,
        unit: str = "celsius",
        fanSpeed: int = 50,
        mode: str = "auto",
    ) -> Dict[str, Union[str, float]]:
        """
        Adjust the climate control of the vehicle.
        
        Args:
            temperature (float): The temperature to set in degrees. Default to celsius.
            unit (str): [Optional] The unit of temperature. [Enum]: ["celsius", "fahrenheit"]
            fanSpeed (int): [Optional] The fan speed to set from 0 to 100. Default is 50.
            mode (str): [Optional] The climate mode to set. [Enum]: ["auto", "cool", "heat", "defrost"]
            
        Returns:
            currentTemperature (float): The current temperature set in degrees Celsius.
            climateMode (str): The current climate mode set.
            humidityLevel (float): The humidity level in percentage.
        """
        if not (0 <= fanSpeed <= 100):
            return {"error": "Fan speed must be between 0 and 100."}
        self.acTemperature = temperature
        if unit == "fahrenheit":
            self.acTemperature = (temperature - 32) * 5 / 9
        self.fanSpeed = fanSpeed
        self.acMode = mode
        return {
            "currentACTemperature": temperature,
            "climateMode": mode,
            "humidityLevel": self.humidityLevel,
        }

    def get_outside_temperature_from_google(self) -> Dict[str, float]:
        """
        Get the outside temperature from Google.
        
        Returns:
            outsideTemperature (float): The outside temperature in degrees Celsius.
        """
        return {"outsideTemperature": self._random.uniform(-10.0, 40.0)}

    def get_outside_temperature_from_weather_com(self) -> Dict[str, float]:
        """
        Get the outside temperature from weather.com.
        
        Returns:
            outsideTemperature (float): The outside temperature in degrees Celsius.
        """
        return {"error": 404}

    def setHeadlights(self, mode: str) -> Dict[str, str]:
        """
        Set the headlights of the vehicle.
        
        Args:
            mode (str): The mode of the headlights. [Enum]: ["on", "off", "auto"]
            
        Returns:
            headlightStatus (str): The status of the headlights. [Enum]: ["on", "off"]
        """
        if mode not in ["on", "off", "auto"]:
            return {"error": "Invalid headlight mode."}
        if mode == "on":
            self.headLightStatus = "on"
            return {"headlightStatus": "on"}
        else:
            self.headLightStatus = "off"
            return {"headlightStatus": "off"}
    
    def displayCarStatus(self, option: str) -> Dict[str, Union[str, float, Dict[str, str]]]:
        """
        Display the status of the vehicle based on the provided display option.
        
        Args:
            option (str): The option to display. [Enum]: ["fuel", "battery", "doors", "climate", "headlights", "parkingBrake", "brakePedal", "engine"]
            
        Returns:
            status (Dict): The status of the vehicle based on the option.
        """
        status = {}
        if option == "fuel":
            status["fuelLevel"] = self.fuelLevel
        elif option == "battery":
            status["batteryVoltage"] = self.batteryVoltage
        elif option == "doors":
            status["doorStatus"] = self.doorStatus
        elif option == "climate":
            status["currentACTemperature"] = self.acTemperature
            status["fanSpeed"] = self.fanSpeed
            status["climateMode"] = self.acMode
            status["humidityLevel"] = self.humidityLevel
        elif option == "headlights":
            status["headlightStatus"] = self.headLightStatus
        elif option == "parkingBrake":
            status["parkingBrakeStatus"] = self.parkingBrakeStatus
            status["parkingBrakeForce"] = self._parkingBrakeForce
            status["slopeAngle"] = self._slopeAngle
        elif option == "brakePedal":
            status["brakePedalStatus"] = self.brakePedalStatus
            status["brakePedalForce"] = self._brakePedalForce
        elif option == "engine":
            status["engineState"] = self.engine_state
        else:
            status["error"] = "Invalid option"
        return status

    def activateParkingBrake(self, mode: str) -> Dict[str, Union[str, float]]:
        """
        Activate or release the parking brake of the vehicle.
        
        Args:
            mode (str): The mode to set. [Enum]: ["engage", "release"]
            
        Returns:
            parkingBrakeStatus (str): The status of the brake. [Enum]: ["engaged", "released"]
            _parkingBrakeForce (float): The force applied to the brake in Newtons.
            _slopeAngle (float): The slope angle in degrees.
        """
        if mode not in ["engage", "release"]:
            return {"error": "Invalid mode"}
        if mode == "engage":
            self.parkingBrakeStatus = "engaged"
            self._parkingBrakeForce = 500.0
            self._slopeAngle = 10.0
            return {
                "parkingBrakeStatus": "engaged",
                "_parkingBrakeForce": 500.0,
                "_slopeAngle": 10.0
            }
        else:
            self.parkingBrakeStatus = "released"
            self._parkingBrakeForce = 0.0
            self._slopeAngle = 10.0
            return {
                "parkingBrakeStatus": "released",
                "_parkingBrakeForce": 0.0,
                "_slopeAngle": 10.0
            }

    def pressBrakePedal(self, pedalPosition: float) -> Dict[str, Union[str, float]]:
        """
        Press the brake pedal based on pedal position. The brake pedal will be kept pressed until released.

        Args:
            pedalPosition (float): Position of the brake pedal, between 0 (not pressed) and 1 (fully pressed).
            
        Returns:
            brakePedalStatus (str): The status of the brake pedal. [Enum]: ["pressed", "released"]
            brakePedalForce (float): The force applied to the brake pedal in Newtons.
        """
        # Validate pedal position is within 0 to 1
        if not (0 <= pedalPosition <= 1):
            return {"error": "Pedal position must be between 0 and 1."}

        # Release the brake if pedal position is zero
        if pedalPosition == 0:
            self.brakePedalStatus = "released"
            self._brakePedalForce = 0.0
            return {"brakePedalStatus": "released", "brakePedalForce": 0.0}

        # Calculate force based on pedal position
        max_brake_force = 1000  # Max force in Newtons
        force = pedalPosition * max_brake_force

        # Update the brake pedal status and force
        self.brakePedalStatus = "pressed"
        self._brakePedalForce = force
        return {"brakePedalStatus": "pressed", "brakePedalForce": float(force)}

    def releaseBrakePedal(self) -> Dict[str, Union[str, float]]:
        """
        Release the brake pedal of the vehicle.
        
        Returns:
            brakePedalStatus (str): The status of the brake pedal. [Enum]: ["pressed", "released"]
            brakePedalForce (float): The force applied to the brake pedal in Newtons.
        """
        self.brakePedalStatus = "released"
        self._brakePedalForce = 0.0
        return {"brakePedalStatus": "released", "brakePedalForce": 0.0}

    def setCruiseControl(
        self, speed: float, activate: bool, distanceToNextVehicle: float
    ) -> Dict[str, Union[str, float]]:
        """
        Set the cruise control of the vehicle.
        
        Args:
            speed (float): The speed to set in mph. The speed should be between 0 and 120 and a multiple of 5.
            activate (bool): True to activate the cruise control, False to deactivate.
            distanceToNextVehicle (float): The distance to the next vehicle in meters.
            
        Returns:
            cruiseStatus (str): The status of the cruise control. [Enum]: ["active", "inactive"]
            currentSpeed (float): The current speed of the vehicle in mph.
            distanceToNextVehicle (float): The distance to the next vehicle in meters.
        """
        if self.engine_state == "stopped":
            return {"error": "Start the engine before activating the cruise control."}
        if activate:
            self.distanceToNextVehicle = distanceToNextVehicle
            if speed < 0 or speed > 120 or speed % 5 != 0:
                return {"error": "Invalid speed"}
            self.cruiseStatus = "active"
            return {
                "cruiseStatus": "active",
                "currentSpeed": speed,
                "distanceToNextVehicle": distanceToNextVehicle,
            }
        else:
            self.cruiseStatus = "inactive"
            self.distanceToNextVehicle = distanceToNextVehicle
            return {
                "cruiseStatus": "inactive",
                "currentSpeed": speed,
                "distanceToNextVehicle": distanceToNextVehicle,
            }

    def get_current_speed(self) -> Dict[str, float]:
        """
        Get the current speed of the vehicle.
        
        Returns:
            currentSpeed (float): The current speed of the vehicle in mph.
        """
        return {"currentSpeed": self._random.uniform(0.0, 120.0)}

    def display_log(self, messages: List[str]) -> Dict[str, List[str]]:
        """
        Display the log messages.
        
        Args:
            messages (List[str]): The list of messages to display.
            
        Returns:
            log (List[str]): The list of messages displayed.
        """
        return {"log": messages}

    def estimate_drive_feasibility_by_mileage(self, distance: float) -> Dict[str, bool]:
        """
        Estimate if the vehicle can drive a given distance based on current fuel.
        
        Args:
            distance (float): The distance to travel in miles.
            
        Returns:
            canDrive (bool): True if the vehicle can drive the distance, False otherwise.
        """
        if self.fuelLevel * MILE_PER_GALLON < distance:
            return {"canDrive": False}
        else:
            return {"canDrive": True}

    def liter_to_gallon(self, liter: float) -> Dict[str, float]:
        """
        Convert liters to gallons.
        
        Args:
            liter (float): The amount of liter to convert.
            
        Returns:
            gallon (float): The amount of gallon converted.
        """
        return {"gallon": liter * 0.264172}

    def gallon_to_liter(self, gallon: float) -> Dict[str, float]:
        """
        Convert gallons to liters.
        
        Args:
            gallon (float): The amount of gallon to convert.
            
        Returns:
            liter (float): The amount of liter converted.
        """
        return {"liter": gallon * 3.78541}

    def estimate_distance(self, cityA: str, cityB: str) -> Dict[str, float]:
        """
        Estimate the distance between two cities using zip codes.
        
        Args:
            cityA (str): The zipcode of the first city.
            cityB (str): The zipcode of the second city.
            
        Returns:
            distance (float): The distance between the two cities in km.
        """
        # Distance lookup table for known city pairs
        distance_map = {
            ("83214", "74532"): 750.0,
            ("74532", "83214"): 750.0,
            ("56108", "62947"): 320.0,
            ("62947", "56108"): 320.0,
            ("71354", "83462"): 450.0,
            ("83462", "71354"): 450.0,
            ("47329", "52013"): 290.0,
            ("52013", "47329"): 290.0,
            ("69238", "51479"): 630.0,
            ("51479", "69238"): 630.0,
            ("94016", "83214"): 980.0,
            ("83214", "94016"): 980.0,
            ("94016", "94704"): 600.0,
            ("94704", "94016"): 600.0,
            ("94704", "08540"): 2550.0,
            ("08540", "94704"): 2550.0,
            ("94016", "08540"): 1950.0,
            ("08540", "94016"): 1950.0,
            ("62947", "47329"): 1053.0,
            ("47329", "62947"): 1053.0,
            ("94016", "62947"): 780.0,
            ("62947", "94016"): 780.0,
            ("74532", "94016"): 880.0,
            ("94016", "74532"): 880.0,
        }
        
        distance = distance_map.get((cityA, cityB))
        if distance is not None:
            return {"distance": distance}
        else:
            return {"error": "distance not found in database."}

    def get_zipcode_based_on_city(self, city: str) -> Dict[str, str]:
        """
        Get the zipcode based on the city name.
        
        Args:
            city (str): The name of the city.
            
        Returns:
            zipcode (str): The zipcode of the city.
        """
        city_map = {
            "Rivermist": "83214",
            "Stonebrook": "74532",
            "Maplecrest": "56108",
            "Silverpine": "62947",
            "Shadowridge": "71354",
            "Sunset Valley": "83462",
            "Oakendale": "47329",
            "Willowbend": "52013",
            "Crescent Hollow": "69238",
            "Autumnville": "51479",
            "San Francisco": "94016",
        }
        
        zipcode = city_map.get(city, "00000")
        return {"zipcode": zipcode}

    def set_navigation(self, destination: str) -> Dict[str, str]:
        """
        Navigate to the destination.
        
        Args:
            destination (str): The destination to navigate in the format of street, city, state.
            
        Returns:
            status (str): The status of the navigation.
        """
        self.destination = destination
        return {"status": "Navigating to " + destination}

    def check_tire_pressure(self) -> Dict[str, Union[float, bool, Dict]]:
        """
        Check the tire pressure of the vehicle.
        
        Returns:
            tirePressure (Dict): The tire pressure of the vehicle with all tire pressures,
                                healthy status, and car info.
        """
        # Healthy standard: average pressure between 30-35 psi
        healthy_tire_pressure = (
            30 <= (
                self.frontLeftTirePressure
                + self.frontRightTirePressure
                + self.rearLeftTirePressure
                + self.rearRightTirePressure
            ) / 4 <= 35
        )

        return {
            "frontLeftTirePressure": self.frontLeftTirePressure,
            "frontRightTirePressure": self.frontRightTirePressure,
            "rearLeftTirePressure": self.rearLeftTirePressure,
            "rearRightTirePressure": self.rearRightTirePressure,
            "healthy_tire_pressure": healthy_tire_pressure,
            "car_info": {},
        }

    def find_nearest_tire_shop(self) -> Dict[str, str]:
        """
        Find the nearest tire shop.
        
        Returns:
            shopLocation (str): The location of the nearest tire shop.
        """
        return {"shopLocation": "456 Oakwood Avenue, Rivermist, 83214"}


class VehicleControlPlugin(BasePlugin):
    """Plugin for the Vehicle Control API.
    
    This plugin provides tools for controlling various aspects of a vehicle including
    engine operations, door management, climate control, lighting, braking systems,
    and navigation with dynamic domain updates and comprehensive validation.
    """
    
    def __init__(self):
        """Initialize the Vehicle Control plugin."""
        super().__init__()

        self.vehicle_api = VehicleControlAPI()
        self._name = "vehicle_control"
        self._description = "Plugin for vehicle control operations"
        self._tools = self._generate_tool_definitions()
        
        # Cache for dynamic domains - invalidated when vehicle state changes
        self._domain_cache = None
        self._state_changing_operations = {
            'startEngine', 'fillFuelTank', 'lockDoors', 'adjustClimateControl',
            'activateParkingBrake', 'pressBrakePedal', 'releaseBrakePedal',
            'setCruiseControl', 'set_navigation'
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
        """Generate tool definitions for the Vehicle Control plugin."""
        # Generate speed values (multiples of 5 from 0 to 120)
        speed_values = list(range(0, 121, 5))
        
        return [
            {
                "name": "startEngine",
                "description": "Start or stop the vehicle engine. PREREQUISITES: All doors must be locked, brake pedal must be fully pressed (1000N force), and fuel tank must not be empty. Check these conditions first using displayCarStatus.",
                "arguments": [
                    {
                        "name": "ignitionMode",
                        "description": "Engine operation mode. Use 'START' to start the engine or 'STOP' to turn it off. Starting requires all safety conditions to be met.",
                        "domain": {
                            "type": "finite",
                            "values": ["START", "STOP"],
                            "importance": 0.9
                        },
                        "required": True
                    }
                ]
            },
            {
                "name": "fillFuelTank",
                "description": "Add fuel to the vehicle's tank. Tank capacity is 50 gallons maximum. Engine must be stopped before refueling. Use this to add fuel to current level, not replace it.",
                "arguments": [
                    {
                        "name": "fuelAmount",
                        "description": "Amount of fuel to ADD to the tank in gallons (0-50). This is additional fuel, not total capacity. Current fuel + this amount cannot exceed 50 gallons.",
                        "domain": {
                            "type": "numeric_range",
                            "values": [0, 50],
                            "importance": 0.8
                        },
                        "required": True
                    }
                ]
            },
            {
                "name": "lockDoors",
                "description": "Lock or unlock specific vehicle doors. IMPORTANT: The 'door' parameter must be a LIST of door names, even for a single door. Example: ['driver'] for one door, ['driver', 'passenger'] for multiple doors.",
                "arguments": [
                    {
                        "name": "unlock",
                        "description": "Door operation mode. Set to true to UNLOCK the specified doors, false to LOCK them. This affects all doors in the list simultaneously.",
                        "domain": {
                            "type": "boolean",
                            "importance": 0.8
                        },
                        "required": True
                    },
                    {
                        "name": "door",
                        "description": "LIST of door names to operate on. MUST BE A LIST FORMAT: ['door_name'] or ['door1', 'door2']. Valid door names are: 'driver', 'passenger', 'rear_left', 'rear_right'. Example: ['driver', 'passenger'] to operate on front doors.",
                        "domain": {
                            "type": "list",
                            "element_domain": {
                                "type": "finite",
                                "values": ["driver", "passenger", "rear_left", "rear_right"]
                            },
                            "importance": 0.9
                        },
                        "required": True
                    }
                ]
            },
            {
                "name": "adjustClimateControl",
                "description": "Control the vehicle's heating, ventilation, and air conditioning system. Adjusts temperature, fan speed, and operating mode for passenger comfort.",
                "arguments": [
                    {
                        "name": "temperature",
                        "description": "Target temperature to set (-10 to 50). Default unit is Celsius unless specified otherwise in the unit parameter.",
                        "domain": {
                            "type": "numeric_range",
                            "values": [-10, 50],
                            "importance": 0.8
                        },
                        "required": True
                    },
                    {
                        "name": "unit",
                        "description": "Temperature unit for the input value. 'celsius' for Celsius degrees (default), 'fahrenheit' for Fahrenheit degrees. System internally converts to Celsius.",
                        "domain": {
                            "type": "finite",
                            "values": ["celsius", "fahrenheit"],
                            "importance": 0.6
                        },
                        "required": False,
                        "default": "celsius"
                    },
                    {
                        "name": "fanSpeed",
                        "description": "Fan speed percentage (0-100). 0 turns fan off, 100 is maximum speed. Default is 50 for moderate airflow.",
                        "domain": {
                            "type": "numeric_range",
                            "values": [0, 100],
                            "importance": 0.6
                        },
                        "required": False,
                        "default": 50
                    },
                    {
                        "name": "mode",
                        "description": "Climate control mode. 'auto' for automatic temperature control, 'cool' for air conditioning, 'heat' for heating, 'defrost' for windshield defogging.",
                        "domain": {
                            "type": "finite",
                            "values": ["auto", "cool", "heat", "defrost"],
                            "importance": 0.7
                        },
                        "required": False,
                        "default": "auto"
                    }
                ]
            },
            {
                "name": "get_outside_temperature_from_google",
                "description": "Retrieve current outside temperature from Google weather service. Returns temperature in Celsius for climate control reference.",
                "arguments": []
            },
            {
                "name": "get_outside_temperature_from_weather_com",
                "description": "Retrieve current outside temperature from weather.com service. Alternative weather source that may return different data or errors.",
                "arguments": []
            },
            {
                "name": "setHeadlights",
                "description": "Control the vehicle's headlight system. Manages front lighting for visibility and safety during driving.",
                "arguments": [
                    {
                        "name": "mode",
                        "description": "Headlight control mode. 'on' forces headlights on, 'off' turns them off, 'auto' enables automatic control based on ambient light conditions.",
                        "domain": {
                            "type": "finite",
                            "values": ["on", "off", "auto"],
                            "importance": 0.8
                        },
                        "required": True
                    }
                ]
            },
            {
                "name": "displayCarStatus",
                "description": "Show current status of various vehicle systems. Use this to check system states before performing operations or when troubleshooting issues.",
                "arguments": [
                    {
                        "name": "option",
                        "description": "Which system status to display. Options: 'fuel' (tank level), 'battery' (voltage), 'doors' (lock status), 'climate' (AC settings), 'headlights' (light status), 'parkingBrake' (brake state), 'brakePedal' (pedal position), 'engine' (running state).",
                        "domain": {
                            "type": "finite",
                            "values": ["fuel", "battery", "doors", "climate", "headlights", "parkingBrake", "brakePedal", "engine"],
                            "importance": 0.8
                        },
                        "required": True
                    }
                ]
            },
            {
                "name": "activateParkingBrake",
                "description": "Control the parking brake system. Use to secure the vehicle when parked or release for driving. Provides additional safety beyond the brake pedal.",
                "arguments": [
                    {
                        "name": "mode",
                        "description": "Parking brake operation. 'engage' to apply the parking brake (500N force), 'release' to disengage it (0N force). Engaging is recommended when parked.",
                        "domain": {
                            "type": "finite",
                            "values": ["engage", "release"],
                            "importance": 0.8
                        },
                        "required": True
                    }
                ]
            },
            {
                "name": "pressBrakePedal",
                "description": "Apply the brake pedal with specific force. Controls vehicle braking and is required for engine starting. Pedal remains pressed until released or repositioned.",
                "arguments": [
                    {
                        "name": "pedalPosition",
                        "description": "Brake pedal pressure as decimal (0.0-1.0). 0.0 = not pressed, 1.0 = fully pressed (1000N force). Engine starting requires 1.0 (full pressure). Values between represent partial braking.",
                        "domain": {
                            "type": "numeric_range",
                            "values": [0, 1],
                            "importance": 0.8
                        },
                        "required": True
                    }
                ]
            },
            {
                "name": "releaseBrakePedal",
                "description": "Completely release the brake pedal. Sets brake force to 0N and changes status to 'released'. Use when ready to drive or no longer need braking.",
                "arguments": []
            },
            {
                "name": "setCruiseControl",
                "description": "Configure cruise control system for maintaining constant speed. Engine must be running to activate. Speed must be in multiples of 5 mph between 0-120.",
                "arguments": [
                    {
                        "name": "speed",
                        "description": "Target cruise speed in mph. MUST be a multiple of 5 (0, 5, 10, 15... up to 120). Invalid speeds will be rejected. Use 0 with activate=false to turn off cruise control.",
                        "domain": {
                            "type": "finite",
                            "values": speed_values,
                            "importance": 0.8
                        },
                        "required": True
                    },
                    {
                        "name": "activate",
                        "description": "Cruise control state. True to activate cruise control at specified speed, false to deactivate it. Engine must be running to activate.",
                        "domain": {
                            "type": "boolean",
                            "importance": 0.8
                        },
                        "required": True
                    },
                    {
                        "name": "distanceToNextVehicle",
                        "description": "Distance to the vehicle ahead in meters (0-1000). Used for adaptive cruise control and collision avoidance. Higher values provide more following distance.",
                        "domain": {
                            "type": "numeric_range",
                            "values": [0, 1000],
                            "importance": 0.7
                        },
                        "required": True
                    }
                ]
            },
            {
                "name": "get_current_speed",
                "description": "Get the vehicle's current speed in mph. Returns real-time speed information for monitoring and cruise control setup.",
                "arguments": []
            },
            {
                "name": "display_log",
                "description": "Show system log messages for debugging and monitoring. Displays a list of status messages or events from vehicle systems.",
                "arguments": [
                    {
                        "name": "messages",
                        "description": "LIST of message strings to display. MUST BE A LIST FORMAT: ['message1', 'message2']. Each message should be a string describing a system event or status.",
                        "domain": {
                            "type": "list",
                            "element_domain": {
                                "type": "string"
                            },
                            "importance": 0.7
                        },
                        "required": True
                    }
                ]
            },
            {
                "name": "estimate_drive_feasibility_by_mileage",
                "description": "Calculate if the vehicle can complete a trip based on current fuel level and distance. Uses 20 miles per gallon fuel efficiency for estimation.",
                "arguments": [
                    {
                        "name": "distance",
                        "description": "Trip distance in miles (0-10,000). System calculates if current fuel level can cover this distance at 20 MPG efficiency.",
                        "domain": {
                            "type": "numeric_range",
                            "values": [0, 10000],
                            "importance": 0.8
                        },
                        "required": True
                    }
                ]
            },
            {
                "name": "liter_to_gallon",
                "description": "Convert fuel volume from liters to gallons using standard conversion rate. Useful for fuel calculations with metric measurements.",
                "arguments": [
                    {
                        "name": "liter",
                        "description": "Volume in liters to convert to gallons (0-1000). Uses conversion factor of 1 liter = 0.264172 gallons.",
                        "domain": {
                            "type": "numeric_range",
                            "values": [0, 1000],
                            "importance": 0.6
                        },
                        "required": True
                    }
                ]
            },
            {
                "name": "gallon_to_liter",
                "description": "Convert fuel volume from gallons to liters using standard conversion rate. Useful for fuel calculations with imperial measurements.",
                "arguments": [
                    {
                        "name": "gallon",
                        "description": "Volume in gallons to convert to liters (0-1000). Uses conversion factor of 1 gallon = 3.78541 liters.",
                        "domain": {
                            "type": "numeric_range",
                            "values": [0, 1000],
                            "importance": 0.6
                        },
                        "required": True
                    }
                ]
            },
            {
                "name": "estimate_distance",
                "description": "Calculate distance between two cities using their ZIP codes. Returns distance in kilometers for trip planning and fuel estimation.",
                "arguments": [
                    {
                        "name": "cityA",
                        "description": "ZIP code of the starting city. Must be from available ZIP codes: 83214, 74532, 56108, 62947, 71354, 83462, 47329, 52013, 69238, 51479, 94016, 94704, 08540.",
                        "domain": {
                            "type": "finite",
                            "values": ["83214", "74532", "56108", "62947", "71354", "83462", 
                                    "47329", "52013", "69238", "51479", "94016", "94704", "08540"],
                            "importance": 0.8
                        },
                        "required": True
                    },
                    {
                        "name": "cityB",
                        "description": "ZIP code of the destination city. Must be from the same list as cityA. Both cities must have a route in the distance database.",
                        "domain": {
                            "type": "finite",
                            "values": ["83214", "74532", "56108", "62947", "71354", "83462",
                                    "47329", "52013", "69238", "51479", "94016", "94704", "08540"],
                            "importance": 0.8
                        },
                        "required": True
                    }
                ]
            },
            {
                "name": "get_zipcode_based_on_city",
                "description": "Look up the ZIP code for a city name. Use this to get ZIP codes needed for distance estimation between cities.",
                "arguments": [
                    {
                        "name": "city",
                        "description": "City name to look up. Available cities: Rivermist, Stonebrook, Maplecrest, Silverpine, Shadowridge, Sunset Valley, Oakendale, Willowbend, Crescent Hollow, Autumnville, San Francisco.",
                        "domain": {
                            "type": "finite",
                            "values": ["Rivermist", "Stonebrook", "Maplecrest", "Silverpine", "Shadowridge",
                                    "Sunset Valley", "Oakendale", "Willowbend", "Crescent Hollow", "Autumnville", 
                                    "San Francisco"],
                            "importance": 0.8
                        },
                        "required": True
                    }
                ]
            },
            {
                "name": "set_navigation",
                "description": "Set the destination for the vehicle's navigation system. Input the complete address including street, city, and state for route guidance.",
                "arguments": [
                    {
                        "name": "destination",
                        "description": "Complete destination address in format 'street, city, state' (e.g., '123 Main St, Springfield, CA'). Include street address, city name, and state for accurate navigation.",
                        "domain": {
                            "type": "string",
                            "importance": 0.8
                        },
                        "required": True
                    }
                ]
            },
            {
                "name": "check_tire_pressure",
                "description": "Check the air pressure in all four tires and overall tire health. Returns pressure readings for each tire and health status. Healthy range is 30-35 PSI average.",
                "arguments": []
            },
            {
                "name": "find_nearest_tire_shop",
                "description": "Locate the closest tire service shop for tire maintenance, repair, or replacement. Returns shop location and contact information.",
                "arguments": []
            }
        ]
        
    def get_tools(self) -> List[Dict[str, Any]]:
        """Get the list of tools provided by this plugin."""
        return self._tools

    def _invalidate_domain_cache(self):
        """Invalidate the domain cache when vehicle state changes."""
        self._domain_cache = None
    
    def _update_dynamic_domains(self) -> Dict[str, Any]:
        """Update domains based on current vehicle state."""
        if self._domain_cache is not None:
            return self._domain_cache
        
        try:
            updates = {}
            
            # Update fuel amount domain based on current fuel level
            # Can only add fuel up to the tank capacity (50 gallons)
            current_fuel = self.vehicle_api.fuelLevel
            max_additional_fuel = MAX_FUEL_LEVEL - current_fuel
            if max_additional_fuel > 0:
                updates["fillFuelTank.fuelAmount"] = {
                    "type": "numeric_range",
                    "values": [0, max_additional_fuel]
                }
            
            # Update door operations based on current door status
            locked_doors = [door for door, status in self.vehicle_api.doorStatus.items() 
                           if status == "locked"]
            unlocked_doors = [door for door, status in self.vehicle_api.doorStatus.items() 
                             if status == "unlocked"]
            
            # For locking doors - can only lock unlocked doors
            if unlocked_doors:
                updates["lockDoors.door"] = {
                    "type": "list",
                    "element_domain": {
                        "type": "finite",
                        "values": unlocked_doors
                    }
                }
            
            # Update cruise control based on engine state
            # Cruise control can only be activated if engine is running
            if self.vehicle_api.engine_state == "stopped":
                updates["setCruiseControl.activate"] = {
                    "type": "finite",
                    "values": [False]  # Can only deactivate if engine is stopped
                }
            
            # Cache the result
            self._domain_cache = updates
            return updates
            
        except Exception as e:
            logger.error(f"Error updating dynamic domains: {e}")
            return {}
    
    def initialize_from_config(self, config_data: Dict[str, Any]) -> bool:
        """Initialize the vehicle control system from configuration data."""
        if "VehicleControlAPI" in config_data:
            vehicle_config = config_data["VehicleControlAPI"]
            self.vehicle_api._load_scenario(vehicle_config)
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
            # Call the corresponding method on the vehicle API
            vehicle_method = getattr(self.vehicle_api, tool_name)
            result = vehicle_method(**casted_params)
            
            # Invalidate domain cache if this was a state-changing operation
            if tool_name in self._state_changing_operations:
                self._invalidate_domain_cache()
            
            # Handle different result formats
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
                
                # Validate based on domain type
                domain = arg_def.get("domain", {})
                domain_type = domain.get("type", "string")
                
                if domain_type == "numeric_range":
                    try:
                        val = float(value)
                        start, end = domain.get("values", [float('-inf'), float('inf')])
                        if not (start <= val <= end):
                            return False, f"Value {value} for {arg_def['name']} is out of range [{start}, {end}]"
                    except (ValueError, TypeError):
                        return False, f"Invalid numeric value for {arg_def['name']}: {value}"
                
                elif domain_type == "finite":
                    # Get dynamic domain values if available
                    dynamic_domains = self._update_dynamic_domains()
                    domain_key = f"{tool_name}.{arg_def['name']}"
                    if domain_key in dynamic_domains:
                        valid_values = dynamic_domains[domain_key].get("values", [])
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
                    
                    # Validate list elements if element_domain is specified
                    element_domain = domain.get("element_domain")
                    if element_domain:
                        element_type = element_domain.get("type", "string")
                        if element_type == "finite":
                            valid_element_values = element_domain.get("values", [])
                            for element in value:
                                if element not in valid_element_values:
                                    element_values_str = ", ".join(str(v) for v in valid_element_values)
                                    return False, f"Invalid list element {element} for {arg_def['name']}. Expected one of: {element_values_str}"
        
        # Additional custom validations
        if tool_name == "setCruiseControl":
            # Check if engine is running for cruise control activation
            if parameters.get("activate", False) and self.vehicle_api.engine_state == "stopped":
                return False, "Cannot activate cruise control when engine is stopped"
        
        if tool_name == "startEngine":
            # Check engine start conditions
            if parameters.get("ignitionMode") == "START":
                if self.vehicle_api.remainingUnlockedDoors > 0:
                    return False, "All doors must be locked before starting the engine"
                if self.vehicle_api.brakePedalStatus != "pressed":
                    return False, "Brake pedal must be pressed when starting the engine"
                if self.vehicle_api.fuelLevel <= 0:
                    return False, "Cannot start engine with empty fuel tank"
        
        return True, None
    
    def get_domain_updates_from_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Update tool domains based on context."""
        # Initialize from config if available
        if "initial_config" in context and hasattr(self, "initialize_from_config"):
            self.initialize_from_config(context["initial_config"])
        
        # Return dynamic domain updates
        return self._update_dynamic_domains()
    
    def get_uncertainty_context(self) -> Dict[str, Any]:
        """Get vehicle-specific context for uncertainty calculation."""
        try:
            return {
                "engine_state": self.vehicle_api.engine_state,
                "fuel_level": self.vehicle_api.fuelLevel,
                "door_status": self.vehicle_api.doorStatus,
                "unlocked_doors": self.vehicle_api.remainingUnlockedDoors,
                "brake_pedal_status": self.vehicle_api.brakePedalStatus,
                "brake_pedal_force": self.vehicle_api._brakePedalForce,
                "cruise_status": self.vehicle_api.cruiseStatus,
                "parking_brake_status": self.vehicle_api.parkingBrakeStatus,
                "climate_mode": self.vehicle_api.acMode,
                "headlight_status": self.vehicle_api.headLightStatus
            }
        except Exception as e:
            logger.error(f"Error getting uncertainty context: {e}")
            return {}
    
    def get_prompt_templates(self) -> Dict[str, str]:
        """Get vehicle control-specific prompt templates."""
        return {
            "tool_selection": """
You are an AI assistant that helps users with vehicle control operations.

Conversation history:
{conversation_history}

User query: "{user_query}"

Available tools:
{tool_descriptions}

Please analyze the user's query and determine which tool(s) should be called to fulfill the request.
For each tool, specify all required parameters. If a parameter is uncertain, use "<UNK>" as the value.

Consider vehicle safety requirements:
- Engine must be stopped to fill fuel tank
- All doors must be locked and brake pedal fully pressed to start engine
- Engine must be running to activate cruise control
- Brake pedal position affects engine starting (must be fully pressed for start)

Think through this step by step:
1. What vehicle operation is the user requesting?
2. What are the prerequisites for this operation (engine state, door locks, etc.)?
3. Which vehicle control tool(s) are needed to complete this task?
4. What parameters are needed for each tool?
5. Which parameters can be determined from the query, and which are uncertain?

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
You are an AI assistant that helps users with vehicle control operations.

Conversation history:
{conversation_history}

Original user query: "{user_query}"

I've determined that the following tool calls are needed, but some arguments are uncertain:

Tool Calls:
{tool_calls}

Uncertain Arguments:
{uncertain_args}

Your task is to generate clarification questions that would help resolve the uncertainty about specific arguments.

Consider the context of vehicle control:
- Speed settings for cruise control (must be multiples of 5 mph, 0-120)
- Door selection (driver, passenger, rear_left, rear_right)
- Climate control preferences (temperature, fan speed, mode)
- Safety considerations (fuel amounts, brake pedal positions)

Instructions:
1. Generate questions that are clear, specific, and directly address the uncertain arguments
2. Each question should target one or more specific arguments
3. Questions should be conversational and include relevant context about vehicle operations
4. For each question, specify which tool and argument(s) it aims to clarify

Return your response as a JSON object with the following structure:
{
  "questions": [
    {
      "question": "A clear question to ask the user about vehicle operations",
      "target_args": [["tool_name", "arg_name"], ["tool_name", "other_arg_name"]]
    }
  ]
}
"""
        }
    
