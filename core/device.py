"""Device Registry - Cross-device state management."""

from typing import Optional
from datetime import datetime, timezone
from pydantic import BaseModel
import json


class DeviceCapabilities(BaseModel):
    input: list[str] = ["text"]
    output: list[str] = ["text"]
    compute: str = "none"       # none | edge | cloud
    display: str = "medium"     # none | small | medium | large
    sensors: list[str] = []


class DeviceStatus(BaseModel):
    online: bool = False
    battery: int = 100
    focus: bool = False
    last_seen: str = ""


class DeviceInfo(BaseModel):
    id: str
    user_id: str
    name: str
    device_type: str       # desktop | phone | tablet | watch | web
    platform: str          # macos | ios | watchos | web | android
    capabilities: DeviceCapabilities = DeviceCapabilities()
    status: DeviceStatus = DeviceStatus()


class DeviceRegistry:
    def __init__(self):
        self._devices: dict[str, DeviceInfo] = {}

    def register(self, device: DeviceInfo):
        device.status.last_seen = datetime.now(timezone.utc).isoformat()
        self._devices[device.id] = device

    def unregister(self, device_id: str):
        self._devices.pop(device_id, None)

    def get(self, device_id: str) -> Optional[DeviceInfo]:
        return self._devices.get(device_id)

    def get_user_devices(self, user_id: str) -> list[DeviceInfo]:
        return [d for d in self._devices.values() if d.user_id == user_id]

    def get_online_devices(self, user_id: str) -> list[DeviceInfo]:
        return [d for d in self._devices.values() if d.user_id == user_id and d.status.online]

    def update_status(self, device_id: str, status: DeviceStatus):
        device = self._devices.get(device_id)
        if device:
            device.status = status
            device.status.last_seen = datetime.now(timezone.utc).isoformat()

    def get_focused_device(self, user_id: str) -> Optional[DeviceInfo]:
        for d in self._devices.values():
            if d.user_id == user_id and d.status.focus:
                return d
        return None


device_registry = DeviceRegistry()
