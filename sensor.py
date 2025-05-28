import logging
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.components.sensor import SensorEntity
from homeassistant.util import dt as dt_util  # ← Required for timestamp attribute
from .const import DOMAIN, CONF_MAC_ADDRESS


_LOGGER = logging.getLogger(__name__)

SENSOR_TYPES = {
    "temperature":    ("Temperature",    "°C"),
    "humidity":       ("Humidity",       "%"),
    "battery":        ("Battery",        "%"),
    "light":          ("Light",          "lx"),
    "soil_moisture":  ("Soil Moisture",  "%"),
    "aqi":            ("AQI",            None),
    "tvoc":           ("TVOC",           "ppb"),
    "eco2":           ("eCO₂",           "ppm"),
}

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    entities = [
        SensorNodeSensor(coordinator, entry, key, name, unit)
        for key, (name, unit) in SENSOR_TYPES.items()
    ]
    async_add_entities(entities, update_before_add=True)

class SensorNodeSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, entry, key, name, unit):
        super().__init__(coordinator)
        mac = entry.data[CONF_MAC_ADDRESS]
        self._key = key
        self._attr_name = f"{coordinator.device_name} {name}"
        self._attr_native_unit_of_measurement = unit
        self._attr_unique_id = f"{mac}_{key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, mac)},
            name=coordinator.device_name,
        )

    @property
    def native_value(self):
        value = self.coordinator.data.get(self._key)
        _LOGGER.debug("Sensor '%s' key='%s' -> value=%s", self.name, self._key, value)
        return value  # Keep None if you want graphs + state consistency

    @property
    def extra_state_attributes(self):
        return {
            "last_update": self.coordinator.data.get("last_updated")
        }
    @property
    def available(self):
        # Stay available as long as we’ve seen at least one valid value
        return self.native_value is not None
