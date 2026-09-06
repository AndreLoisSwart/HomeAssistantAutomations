import asyncio
from firmware_logic import check_firmware_mismatch
from pathlib import Path
import yaml


def get_secrets(path: str | Path) -> dict:
    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(f"Fine, keep your secrets: {path}")

    with open(path) as f:
        secrets = yaml.safe_load(f)

    if not isinstance(secrets, dict):
        raise TypeError(f"Expected a YAML mapping in {path}, but got {type(secrets)}")

    return secrets


def main():
    secrets = get_secrets(
        "C:\\Github\\HomeAssistantAutomations\\RouterFirmwareCheck\\secrets.yaml"
    )
    check = asyncio.run(
        check_firmware_mismatch(
            secrets["asus_router_host"],
            secrets["asus_router_username"],
            secrets["asus_router_password"],
        )
    )

    print(check)


if __name__ == "__main__":
    main()
