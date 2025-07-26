import math


class PowerReport:
    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(PowerReport, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not PowerReport._initialized:
            # Static variables to store the latest current and tension values
            self._latest_current = None
            self._latest_tension = None
            self._latest_power = None
            self._latest_power_factor = None
            PowerReport._initialized = True

    def convert_in_new_status(self, data):
        """
        Calculate power and power factor when receiving current or tension data.
        This method should be called with either current or tension data.
        """
        # Check if this is current data
        if "current" in data:
            self._latest_current = data["current"]
            return self._update_power_calculations()
        # Check if this is tension/voltage data
        elif "tension" in data or "voltage" in data:
            voltage_value = data.get("tension") or data.get("voltage")
            self._latest_tension = voltage_value
            return self._update_power_calculations()

        # Return the latest calculated values
        return None

    def _update_power_calculations(self):
        """
        Update power and power factor calculations when both current and tension are available
        """
        if self._latest_current is not None and self._latest_tension is not None:
            # Calculate apparent power (S = V * I)
            self._latest_power = self._latest_current * self._latest_tension

            default_power_factor = 86.7
            self._latest_power_factor = default_power_factor

            self._latest_current = None
            self._latest_tension = None

            return [{
                "name": "Power",
                "value": self._latest_power,
            },
                {
                "name": "PowerFactor",
                "value": self._latest_power_factor
            }]
