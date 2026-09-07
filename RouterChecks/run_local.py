import asyncio

from firmware_logic import check_firmware_mismatch
from router_helpers import get_secrets
from speed_test_logic import (
    build_speedtest_config,
    get_speed_test_data,
    trigger_speed_test,
    parse_speedtest_result,
)

PATH_HOME = "C:\\Github\\HomeAssistantAutomations\\RouterChecks\\secrets.yaml"
PATH_WORK = "C:\\Andre\\HomeAssistantAutomations\\RouterChecks\\secrets.yaml"

PATH = PATH_WORK


def main_firmware_logic():
    secrets = get_secrets(PATH)
    check = asyncio.run(
        check_firmware_mismatch(
            secrets["asus_router_host"],
            secrets["asus_router_username"],
            secrets["asus_router_password"],
        )
    )

    print(check)


def main_speed_test_logic():
    secrets = get_secrets(PATH)

    config = build_speedtest_config(
        secrets["asus_router_host"],
        secrets["asus_router_username"],
        secrets["asus_router_password"],
    )
    asyncio.run(trigger_speed_test(config))

    data = asyncio.run(
        get_speed_test_data(
            secrets["asus_router_host"],
            secrets["asus_router_username"],
            secrets["asus_router_password"],
        )
    )

    print(parse_speedtest_result(data))


def main():
    # main_firmware_logic()  ## Run to test firmware logic
    main_speed_test_logic()  ## Run to test speed test logic


if __name__ == "__main__":
    main()
