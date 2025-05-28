from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.components.binary_sensor import BinarySensorEntity
from .const import DOMAIN, CONF_MAC_ADDRESS

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        [BLENodeConnectedBinarySensor(coordinator, entry)],
        update_before_add=True
    )

class BLENodeConnectedBinarySensor(CoordinatorEntity, BinarySensorEntity):
    def __init__(self, coordinator, entry):
        super().__init__(coordinator)
        mac = entry.data[CONF_MAC_ADDRESS]
        self._attr_name = f"{mac} Connected"
        self._attr_unique_id = f"{mac}_connected"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, mac)},
            name=coordinator.device_name,
        )

    @property
    def is_on(self):
        return bool(self.coordinator.data.get("is_connected"))

    @property
    def available(self):
        # Always show the sensor as available, even if BLE is offline
        return True

    @property
    def extra_state_attributes(self):
        return {
            "last_checked": self.coordinator.data.get("last_updated")
        }
