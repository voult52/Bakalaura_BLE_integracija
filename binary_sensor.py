from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.components.binary_sensor import BinarySensorEntity
from .const import DOMAIN, CONF_MAC_ADDRESS

# Asinhrona funkcija, kas pievieno bināro sensoru Home Assistant sistēmā
async def async_setup_entry(hass, entry, async_add_entities):
    # Iegūst koordinatoru, kas atbild par datu atjaunināšanu
    coordinator = hass.data[DOMAIN][entry.entry_id]

    # Pievieno vienu bināro sensoru entitāti, pirms pievienošanas atjaunina tās stāvokli
    async_add_entities(
        [BLENodeConnectedBinarySensor(coordinator, entry)],
        update_before_add=True
    )

# Binārais sensors, kas pārstāv BLE ierīces savienojuma statusu
class BLENodeConnectedBinarySensor(CoordinatorEntity, BinarySensorEntity):
    def __init__(self, coordinator, entry):
        super().__init__(coordinator)
        mac = entry.data[CONF_MAC_ADDRESS]

        # Nosaka sensora nosaukumu un unikālo ID, izmantojot MAC adresi
        self._attr_name = f"{mac} Connected"
        self._attr_unique_id = f"{mac}_connected"

        # Iestata ierīces informāciju, lai Home Assistant to varētu sasaistīt ar ierīci
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, mac)},  # Unikāls identifikators šai ierīcei
            name=coordinator.device_name,  # Ierīces nosaukums no koordinatora
        )

    # Atgriež `True`, ja ierīce ir savienota, balstoties uz koordinatora datiem
    @property
    def is_on(self):
        return bool(self.coordinator.data.get("is_connected"))

    # Atgriež `True`, lai sensors vienmēr būtu redzams kā pieejams
    @property
    def available(self):
        return True

    # Papildu atribūti, kurus parādīt sensora statusā
    @property
    def extra_state_attributes(self):
        return {
            "last_checked": self.coordinator.data.get("last_updated")
        }
