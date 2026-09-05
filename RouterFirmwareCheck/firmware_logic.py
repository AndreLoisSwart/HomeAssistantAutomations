import asyncio
import aiohttp
from asusrouter import AsusRouter, AsusData
import yaml
from typing import NamedTuple


class DeviceInfo(NamedTuple):
    fw: str
    device_type: str


class FirmwareCheckResult(NamedTuple):
    mismatch: bool
    device_info: dict[str, DeviceInfo]


async def check_firmware_mismatch(
    host: str, username: str, password: str
) -> FirmwareCheckResult:
    session = aiohttp.ClientSession()
    router = AsusRouter(
        hostname=host,
        username=username,
        password=password,
        use_ssl=True,
        session=session,
    )
    try:
        await router.async_connect()
        data = await router.async_get_data(AsusData.AIMESH)
    finally:
        await router.async_disconnect()
        await session.close()

    devices = {
        mac: DeviceInfo(fw=device.fw, device_type=device.type)
        for mac, device in data.items()
    }

    fw_versions = {d.fw for d in devices.values()}
    mismatch = len(fw_versions) > 1

    return FirmwareCheckResult(mismatch, devices)
