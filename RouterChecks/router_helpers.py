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
