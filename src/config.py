import json
from json import JSONDecodeError
from pathlib import Path


DEFAULT_CONFIG_FILENAMES = ["smellrc.json", ".smellrc.json"]


def find_config_file(project_path: str, explicit_config: str | None = None) -> Path | None:
    """
    Resolve the configuration file to use.

    Priority:
    1. Explicit --config path
    2. Default config filenames in the analyzed project root
    3. No config found -> return None
    """
    if explicit_config:
        path = Path(explicit_config).expanduser().resolve()

        if not path.exists():
            raise RuntimeError(
                f"Configuration file not found: '{explicit_config}'. "
                "Check the path passed to --config."
            )

        if not path.is_file():
            raise RuntimeError(
                f"Configuration path is not a file: '{explicit_config}'."
            )

        return path

    project_dir = Path(project_path).expanduser().resolve()

    if not project_dir.exists():
        raise RuntimeError(
            f"Project path does not exist: '{project_path}'."
        )

    if not project_dir.is_dir():
        raise RuntimeError(
            f"Project path is not a directory: '{project_path}'."
        )

    for filename in DEFAULT_CONFIG_FILENAMES:
        candidate = project_dir / filename
        if candidate.exists() and candidate.is_file():
            return candidate

    return None


def load_config(project_path: str, explicit_config: str | None = None) -> dict:
    """
    Load configuration from JSON file, or return an empty dict if no config is found.
    """
    config_path = find_config_file(project_path, explicit_config)

    if config_path is None:
        return {}

    try:
        with config_path.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except JSONDecodeError as exc:
        raise RuntimeError(
            f"Configuration file '{config_path}' is not valid JSON "
            f"(line {exc.lineno}, column {exc.colno})."
        ) from exc
    except OSError as exc:
        raise RuntimeError(
            f"Failed to read configuration file '{config_path}': {exc}"
        ) from exc

    if not isinstance(data, dict):
        raise RuntimeError(
            f"Configuration file '{config_path}' must contain a JSON object "
            "at the top level."
        )

    return data