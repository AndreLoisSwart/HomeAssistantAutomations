import configparser
from typing import NamedTuple

import aiohttp
from asusrouter import AsusData, AsusRouter
from asuswrtspeedtest import SpeedtestClient
from router_helpers import convert_speed_test_result


class Ping(NamedTuple):
    jitter: float
    latency: float


class BandwidthResult(NamedTuple):
    megabits_per_second: float
    elapsed: float


class SpeedTestResult(NamedTuple):
    server: str
    download: BandwidthResult
    upload: BandwidthResult
    ping: Ping


async def get_speed_test_data(host: str, username: str, password: str) -> dict:
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


def parse_speedtest_result(data: dict) -> SpeedTestResult:
    return SpeedTestResult(
        server=data["server"]["name"],
        download=BandwidthResult(
            megabits_per_second=convert_speed_test_result(
                data["download"]["bytes"], data["download"]["elapsed"]
            ),
            elapsed=float(data["download"]["elapsed"] / 1000),
        ),
        upload=BandwidthResult(
            megabits_per_second=convert_speed_test_result(
                data["upload"]["bytes"], data["upload"]["elapsed"]
            ),
            elapsed=float(data["upload"]["elapsed"] / 1000),
        ),
        ping=Ping(
            jitter=float(data["ping"]["jitter"]), latency=float(data["ping"]["latency"])
        ),
    )
