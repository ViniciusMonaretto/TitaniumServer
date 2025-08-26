from dataModules.panel import Panel


class PanelGroup:
    id = 0
    name = ""
    panels = list[Panel]

    def __init__(self, name: str, group_id: int = -1):
        self.id = group_id
        self.name = name
        self.panels = []

    def to_json(self):
        return {
            "id": self.id,
            "name": self.name
        }
