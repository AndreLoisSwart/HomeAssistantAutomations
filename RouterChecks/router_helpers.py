from pathlib import Path

import yaml

MEGABITS_CONVERSION_RATE = 125000
MILLISECONDS = 1000


def get_secrets(path: str | Path) -> dict:
    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(f"Fine, keep your secrets: {path}")

    with open(path) as f:
        secrets = yaml.safe_load(f)

    if not isinstance(secrets, dict):
        raise TypeError(f"Expected a YAML mapping in {path}, but got {type(secrets)}")

    return secrets


def convert_speed_test_result(bytes_count: float, elapsed: float) -> float:
    megabits_per_second = (
        bytes_count / (elapsed / MILLISECONDS)
    ) / MEGABITS_CONVERSION_RATE
    return round(megabits_per_second, 2)
