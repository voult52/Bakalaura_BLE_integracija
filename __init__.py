from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .coordinator import SensorNodeDataUpdateCoordinator
from .const import DOMAIN, CONF_MAC_ADDRESS, CONF_CHAR_UUID


# Asinhrona funkcija, kas inicializē konfigurācijas ierakstu (integrāciju)
async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    # Izveido datu atjaunināšanas koordinatoru, izmantojot ierakstā saglabāto MAC adresi un rakstura UUID
    coordinator = SensorNodeDataUpdateCoordinator(
        hass,
        mac_address=entry.data[CONF_MAC_ADDRESS],
        char_uuid=entry.data[CONF_CHAR_UUID],
    )

    # Veic pirmo datu ielādi no sensora
    await coordinator.async_config_entry_first_refresh()

    # Saglabā koordinatoru `hass.data`, lai tas būtu pieejams citiem komponentiem
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    # Pārraida konfigurācijas ierakstu sensoru un bināro sensoru platformām
    await hass.config_entries.async_forward_entry_setups(
        entry, ["sensor", "binary_sensor"]
    )

    return True


# Asinhrona funkcija, kas atbild par konfigurācijas ieraksta noņemšanu
async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    # Aizver sensoru un bināro sensoru platformas, kas saistītas ar šo ierakstu
    unload_ok = await hass.config_entries.async_unload_platforms(
        entry, ["sensor", "binary_sensor"]
    )

    # Ja noņemšana bija veiksmīga, izņem koordinatoru no `hass.data`
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
