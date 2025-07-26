from .power_report import PowerReport

class Tension:
    def __init__(self):
        self.power_report = PowerReport()
    
    def convert_in_new_status(self, data):
        # Convert tension/voltage data if needed
        # Then call PowerReport to calculate power
        return self.power_report.convert_in_new_status(data) 
