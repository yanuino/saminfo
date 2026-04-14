"""Public API for Samsung device communication helpers.

This package exposes detection and AT-channel utilities used by the application.
"""

from .at_client import ATDeviceInfo, enter_download_mode, read_device_info_at, send_at_command
from .detector import DetectedDevice, detect_samsung_devices, get_first_device
from .device_command import enter_odin_mode, is_odin_mode
from .errors import DeviceATError, DeviceError, DeviceNotFoundError, DeviceOdinError

__all__ = [
    "ATDeviceInfo",
    "DetectedDevice",
    "DeviceATError",
    "DeviceError",
    "DeviceNotFoundError",
    "DeviceOdinError",
    "detect_samsung_devices",
    "enter_download_mode",
    "enter_odin_mode",
    "get_first_device",
    "is_odin_mode",
    "read_device_info_at",
    "send_at_command",
]
