from homeassistant.const import Platform

# Integrācijas domēns – izmanto, lai identificētu komponenti Home Assistant sistēmā
DOMAIN = "ble_node"

# Konfigurācijas atslēgas (tiek izmantotas ConfigEntry datu vārdnīcā)
CONF_MAC_ADDRESS = "mac_address"        # BLE ierīces MAC adrese
CONF_SERVICE_UUID = "service_uuid"      # BLE servisa UUID
CONF_CHAR_UUID = "char_uuid"            # BLE rakstura UUID

# Sensora ierīces noteikšanai izmantotie UUID
SERVICE_UUID = "9eca0001-24dc-0ee5-a9e0-93f3a3b52000"       # BLE servisa UUID, kuru meklējam
SENSOR_CHAR_UUID = "9eca0002-24dc-0ee5-a9e0-93f3a3b52000"   # BLE rakstura UUID, no kura nolasīt sensoru datus

# Platformas, kuras šī integrācija atbalsta
PLATFORMS = ["sensor", "binary_sensor"]
