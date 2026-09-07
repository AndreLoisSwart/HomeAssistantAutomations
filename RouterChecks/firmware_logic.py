import asyncio
from typing import NamedTuple

import aiohttp
from asusrouter import AsusData, AsusRouter


class DeviceInfo(NamedTuple):
    fw: str
    device_type: str


class FirmwareCheckResult(NamedTuple):
    mismatch: bool
    device_info: dict[str, DeviceInfo]


async def check_firmware_mismatch(
    host: str, username: str, password: str, retries: int = 2
) -> FirmwareCheckResult:
    last_error: Exception | None = None

    for attempt in range(retries):
        timeout = aiohttp.ClientTimeout(total=15)
        session = aiohttp.ClientSession(timeout=timeout)
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

            devices = {
                mac: DeviceInfo(fw=device.fw, device_type=device.type)
                for mac, device in data.items()
            }
            fw_versions = {d.fw for d in devices.values()}
            mismatch = len(fw_versions) > 1

            return FirmwareCheckResult(mismatch, devices)

        except Exception as e:
            last_error = e
            await asyncio.sleep(2)

        finally:
            await router.async_disconnect()
            await session.close()

    raise last_error
