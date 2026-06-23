"""Constants and attribute maps for the Whirlpool Microwave integration."""

DOMAIN = "whirlpool_microwave"

# Attribute names use the device's real Whirlpool protocol namespaces:
#   Hood_  = hood vent subsystem
#   Mwo_   = microwave oven subsystem
#   Sys_   = system-level (shared) subsystem
# These prefixes are not a naming mistake; they mirror the cloud API.

# Controllable attributes (write + read).
ATTR_LIGHT = "Hood_OperationSetSurfaceLight"
ATTR_FAN = "Hood_OperationSetExhaustFanSpeed"
ATTR_QUIET = "Sys_OperationSetQuietModeEnabled"
ATTR_LOCK = "Sys_OperationSetControlLock"
ATTR_TURNTABLE = "Mwo_CycleSetTurntable"

# Status attributes (read only).
ATTR_DOOR = "Mwo_OperationStatusDoorOpen"
ATTR_IDLE = "Mwo_ModeStatusIdle"
ATTR_COOK_REMAINING = "Mwo_TimeStatusCookTimeRemaining"

# Hood light: HA level name -> device value (string). Confirmed off=0, low=2, high=4.
LIGHT_LEVELS = {"off": "0", "low": "2", "high": "4"}
LIGHT_VALUE_TO_LEVEL = {value: name for name, value in LIGHT_LEVELS.items()}

# Hood fan: ordered slow..fast (excludes off), plus the full name -> value map.
# Confirmed off=0, low=2, medium=4, medium_high=5, high=6.
FAN_ORDERED = ["low", "medium", "medium_high", "high"]
FAN_SPEEDS = {"off": "0", "low": "2", "medium": "4", "medium_high": "5", "high": "6"}
FAN_VALUE_TO_SPEED = {value: name for name, value in FAN_SPEEDS.items()}

# Config entry keys.
CONF_REGION = "region"
CONF_BRAND = "brand"
DEFAULT_REGION = "US"
DEFAULT_BRAND = "Whirlpool"

DEFAULT_SCAN_INTERVAL = 30
