import struct
import logging
from datetime import timedelta
from bleak import BleakClient, BleakError
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class SensorNodeDataUpdateCoordinator(DataUpdateCoordinator):
    SCAN_INTERVAL = 5  # Poll every 10s

    def __init__(self, hass, mac_address: str, char_uuid: str):
        super().__init__(
            hass, _LOGGER,
            name=f"{DOMAIN}_{mac_address}",
            update_interval=timedelta(seconds=self.SCAN_INTERVAL),
        )
        self.client = BleakClient(mac_address)
        self.char_uuid = char_uuid
        self.device_name = mac_address
        self.data = {
            "is_connected": False,
            "last_updated": None,
            "temperature": None,
            "humidity": None,
            "battery": None,
            "light": None,
            "soil_moisture": None,
            "aqi": None,
            "tvoc": None,
            "eco2": None,
        }

    async def _async_update_data(self):
        try:
            _LOGGER.info("Connecting to %s...", self.device_name)
            await self.client.connect(timeout=5.0)

            _LOGGER.info("Connected. Reading characteristic %s", self.char_uuid)
            raw = await self.client.read_gatt_char(self.char_uuid)
            _LOGGER.info("Raw payload [%d bytes]: %s", len(raw), raw.hex())

            if len(raw) < 12:
                _LOGGER.warning("Payload too short (%d bytes)", len(raw))
                self.data["is_connected"] = True
                return self.data

            temp, hum, batt, light, soil, aqi, tvoc, eco2 = struct.unpack("<hhBBBBHH", raw)

            self.data.update({
                "temperature":   temp / 10.0,
                "humidity":      hum / 10.0,
                "battery":       None if batt == 0xFF else batt,
                "light":         None if light == 0xFF else light,
                "soil_moisture": soil,
                "aqi":           None if aqi == 0xFF else aqi,
                "tvoc":          None if tvoc == 0xFFFF else tvoc,
                "eco2":          None if eco2 == 0xFFFF else eco2,
                "is_connected":  True,
                "last_updated":  self.hass.helpers.event.dt_util.utcnow().isoformat()
            })

            _LOGGER.info("Parsed sensor data: %s", self.data)

        except BleakError as err:
            _LOGGER.warning("BLE read failed: %s", err)
            self.data["is_connected"] = False
            # Don't reset last_updated or sensor values

        finally:
            if self.client.is_connected:
                try:
                    await self.client.disconnect()
                except BleakError:
                    _LOGGER.debug("Failed to disconnect BLE client cleanly.")

        return self.data
