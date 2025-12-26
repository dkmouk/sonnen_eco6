DOMAIN = "sonnen_eco6"

CONF_HOST = "host"
CONF_PORT_DATA = "port_data"
CONF_PORT_CTRL = "port_ctrl"
CONF_SCAN_INTERVAL = "scan_interval"
CONF_DEVICE_NUM = "device_num"

DEFAULT_PORT_DATA = 7979
DEFAULT_PORT_CTRL = 3480
DEFAULT_SCAN_INTERVAL = 10
DEFAULT_DEVICE_NUM = 10

# Battery endpoints (your list)
METRICS = {
    "M03": {"name": "Leistung Erzeuger", "unit": "W", "device_class": "power"},
    "M04": {"name": "Hausverbrauch", "unit": "W", "device_class": "power"},
    "M05": {"name": "SOC", "unit": "%", "device_class": "battery"},
    "M06": {"name": "Betriebsart Zahl", "unit": None, "device_class": None},
    "M07": {"name": "Verbrauch Phase L1", "unit": "W", "device_class": "power"},
    "M08": {"name": "Verbrauch Phase L2", "unit": "W", "device_class": "power"},
    "M09": {"name": "Verbrauch Phase L3", "unit": "W", "device_class": "power"},
    "M10": {"name": "Max Verbrauch Phase L1", "unit": "W", "device_class": "power"},
    "M11": {"name": "Max Verbrauch Phase L2", "unit": "W", "device_class": "power"},
    "M12": {"name": "Max Verbrauch Phase L3", "unit": "W", "device_class": "power"},
    "M34": {"name": "Entladeleistung", "unit": "W", "device_class": "power"},
    "M35": {"name": "Ladeleistung", "unit": "W", "device_class": "power"},
}

# Operation modes (your values)
OP_MODES = {
    "Auto": 10,
    "Standby": 20,
    "Laden Auto": 12,
    "Laden Standby": 22,
}
