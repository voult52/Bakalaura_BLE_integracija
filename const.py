from homeassistant.const import Platform

DOMAIN = "ble_node"

CONF_MAC_ADDRESS = "mac_address"
CONF_SERVICE_UUID = "service_uuid"
CONF_CHAR_UUID = "char_uuid"

# ✅ These now match what your ESP32 actually advertises
SERVICE_UUID = "9eca0001-24dc-0ee5-a9e0-93f3a3b52000"
SENSOR_CHAR_UUID = "9eca0002-24dc-0ee5-a9e0-93f3a3b52000"

PLATFORMS = ["sensor", "binary_sensor"]
