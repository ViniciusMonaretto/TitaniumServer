
class PanelTypes:
    ReadPanel = "read"
    WritePanel = "write"
    Unknow = "Unknow"

    @staticmethod
    def GetType(self, panelName):
        if panelName == self.ReadPanel:
            return self.ReadPanel
        elif panelName == self.WritePanel:
            return self.WritePanel
        
        return self.Unknow

class Panel:
    _title = ""
    _status = ""
    _gateway = ""
    _panel_type = PanelTypes.ReadPanel
    def __init__(self, obj):
        self._title = obj["title"]
        self._status = obj["status"]
        self._gateway = obj["gateway"]
        self._panel_type = PanelTypes.GetType(obj["panelType"])