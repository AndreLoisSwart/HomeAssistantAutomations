import asyncio
from firmware_logic import check_firmware_mismatch
from speed_test_logic import (
    get_speed_test_data,
    build_speedtest_config,
    trigger_speed_test,
)
from router_helpers import get_secrets


def main_firmware_logic():
    secrets = get_secrets(
        "C:\\Github\\HomeAssistantAutomations\\RouterChecks\\secrets.yaml"
    )
    check = asyncio.run(
        check_firmware_mismatch(
            secrets["asus_router_host"],
            secrets["asus_router_username"],
            secrets["asus_router_password"],
        )
    )

    print(check)


def main_speed_test_logic():
    secrets = get_secrets(
        "C:\\Github\\HomeAssistantAutomations\\RouterChecks\\secrets.yaml"
    )

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

    print(data)


def main():
    # main_firmware_logic()  ## Run to test firmware logic
    main_speed_test_logic()  ## Run to test speed test logic


if __name__ == "__main__":
    main()
