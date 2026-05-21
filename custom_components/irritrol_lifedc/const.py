"""Constants for the Irritrol LifeDC integration."""

DOMAIN = "irritrol_lifedc"
CONF_ENTITY_PREFIX = "entity_prefix"
DEFAULT_ENTITY_PREFIX = "irritrol_irrigation"
MANUFACTURER = "Irritrol"
MODEL = "LifeDC"

PLATFORMS = ["button", "switch", "number", "sensor", "binary_sensor"]

SERVICE_START_CYCLE = "start_cycle"
SERVICE_STOP = "stop"
SERVICE_NEXT_ZONE = "next_zone"
SERVICE_PAUSE = "pause"
SERVICE_RESUME = "resume"
SERVICE_RUN_ZONE = "run_zone"
