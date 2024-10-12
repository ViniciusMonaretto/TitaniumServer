
class PanelTypes:
    ReadPanel = "read"
    WritePanel = "write"
    Unknow = "Unknow"

    @classmethod
    def GetType(cls, panelName):
        if panelName == cls.ReadPanel:
            return cls.ReadPanel
        elif panelName == cls.WritePanel:
            return cls.WritePanel
        
        return cls.Unknow

class Panel:
    _title = ""
    _gateway = ""
    _topic = ""
    _panel_type = PanelTypes.ReadPanel
    def __init__(self, obj):
        self._title = obj["title"]
        self._gateway = obj["gateway"]
        self._topic = obj["topic"]
        self._panel_type = PanelTypes.GetType(obj["panelType"])