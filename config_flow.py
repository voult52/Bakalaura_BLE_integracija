import asyncio
import logging
import async_timeout
import voluptuous as vol

from bleak import BleakScanner
from homeassistant import config_entries
from homeassistant.components.bluetooth import BluetoothServiceInfoBleak

from .const import (
    DOMAIN,
    CONF_MAC_ADDRESS,
    CONF_SERVICE_UUID,
    CONF_CHAR_UUID,
    SERVICE_UUID,
    SENSOR_CHAR_UUID,
)

_LOGGER = logging.getLogger(__name__)
SCAN_TIMEOUT = 5  # Ierīču meklēšanas taimauts (sekundēs)


# Konfigurācijas plūsmas klase BLE sensoru integrācijai
class BleSensorScannerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1  # Konfigurācijas plūsmas versija
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_POLL  # Savienojuma tips

    def __init__(self):
        self._devices = {}  # Saglabā atrastās ierīces
        self._mac = None  # Saglabā izvēlēto MAC adresi

    # Solis, kas tiek izpildīts automātiskas BLE atklāšanas gadījumā
    async def async_step_bluetooth(self, discovery_info: BluetoothServiceInfoBleak):
        # Pārbauda, vai atklātajā ierīcē ir meklētais servisa UUID
        uuids = [u.lower() for u in (discovery_info.service_uuids or [])]
        if SERVICE_UUID.lower() in uuids:
            self._mac = discovery_info.address
            _LOGGER.info("Auto-detected SensorNode %s", self._mac)

            # Iestata ierīces unikālo ID, lai nepieļautu dubultu pievienošanu
            await self.async_set_unique_id(self._mac.lower())
            self._abort_if_unique_id_configured()

            # Izveido konfigurācijas ierakstu automātiski
            return self.async_create_entry(
                title=self._mac,
                data={
                    CONF_MAC_ADDRESS: self._mac,
                    CONF_SERVICE_UUID: SERVICE_UUID,
                    CONF_CHAR_UUID: SENSOR_CHAR_UUID,
                },
            )

        # Ja UUID neatbilst, turpina ar manuālo soli
        return await self.async_step_user()

    # Lietotāja solis, ja automātiskais neatpazīst vai tiek veikta manuāla konfigurācija
    async def async_step_user(self, user_input=None):
        if user_input is None:
            try:
                # Skatās pēc BLE ierīcēm ar taimautu
                async with async_timeout.timeout(SCAN_TIMEOUT):
                    found = await BleakScanner.discover()
            except asyncio.TimeoutError:
                found = []

            # Saglabā atrastās ierīces vārdā un adresē
            self._devices = {
                d.address: f"{d.name or 'Unknown'} ({d.address})" for d in found
            }

            # Ja nav atrastu ierīču, pārtrauc konfigurāciju
            if not self._devices:
                return self.async_abort(reason="no_devices_found")

            # Parāda formu, kur lietotājs var izvēlēties kādu no atrastajām ierīcēm
            schema = vol.Schema({vol.Required(CONF_MAC_ADDRESS): vol.In(self._devices)})
            return self.async_show_form(
                step_id="user",
                data_schema=schema,
                description_placeholders={"timeout": SCAN_TIMEOUT},
            )

        # Lietotājs izvēlējās ierīci, izveido ierakstu
        self._mac = user_input[CONF_MAC_ADDRESS]
        await self.async_set_unique_id(self._mac.lower())
        self._abort_if_unique_id_configured()

        return self.async_create_entry(
            title=self._mac,
            data={
                CONF_MAC_ADDRESS: self._mac,
                CONF_SERVICE_UUID: SERVICE_UUID,
                CONF_CHAR_UUID: SENSOR_CHAR_UUID,
            },
        )
