import asyncio
import aiohttp
from asusrouter import AsusData, AsusRouter
from typing import NamedTuple
import configparser
from asuswrtspeedtest import SpeedtestClient


async def get_speed_test_data(host: str, username: str, password: str):
    timeout = aiohttp.ClientTimeout(total=15)
    session = aiohttp.ClientSession(timeout=timeout)
    router = AsusRouter(
        hostname=host,
        username=username,
        password=password,
        use_ssl=True,
        session=session,
    )
    await router.async_connect()

    data = await router.async_get_data(AsusData.SPEEDTEST)

    await router.async_disconnect()
    await session.close()

    return data


def build_speedtest_config(
    host: str, username: str, password: str
) -> configparser.ConfigParser:
    config = configparser.ConfigParser()
    config["asus_router"] = {
        "host": host,
        "port": "8443",
        "use_https": "true",
        "username": username,
        "password": password,
    }
    config["speedtest"] = {
        "timeout": "120",
        "poll_frequency": "15",
        "history_limit": "10",
    }
    return config


async def trigger_speed_test(config: configparser.ConfigParser):
    async with SpeedtestClient(config) as speedtest_client:
        await speedtest_client.run()
