from .power_report import PowerReport

class Current:
    def __init__(self):
        self.power_report = PowerReport()
    
    def convert_in_new_status(self, data):
        # Convert current data if needed
        # Then call PowerReport to calculate power
        return self.power_report.convert_in_new_status(data) 
