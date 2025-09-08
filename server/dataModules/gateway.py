class GatewayStatus:
    name: str
    ip: str
    uptime: int

    def to_json(self):
        return {
            "name": self.name,
            "ip": self.ip,
            "uptime": self.uptime
        }
