import json
from pathlib import Path


DEFAULT_CONFIG_FILENAMES = ["smellrc.json", ".smellrc.json"]


def find_config_file(project_path: str, explicit_config: str | None = None) -> Path | None:
    if explicit_config:
        path = Path(explicit_config)
        if not path.exists():
            raise RuntimeError(f"Configuration file not found: {explicit_config}")
        return path

    project_dir = Path(project_path)

    for filename in DEFAULT_CONFIG_FILENAMES:
        candidate = project_dir / filename
        if candidate.exists():
            return candidate

    return None


def load_config(project_path: str, explicit_config: str | None = None) -> dict:
    config_path = find_config_file(project_path, explicit_config)
    if config_path is None:
        return {}

    with config_path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, dict):
        raise RuntimeError("Configuration file must contain a JSON object.")

    return data