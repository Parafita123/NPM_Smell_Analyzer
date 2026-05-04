import json
from pathlib import Path
from typing import Any, Dict


def read_package_json(project_path: str) -> Dict[str, Any]:
    package_json_path = Path(project_path) / "package.json"

    if not package_json_path.exists():
        raise FileNotFoundError(f"package.json not found in: {project_path}")

    with package_json_path.open("r", encoding="utf-8") as f:
        return json.load(f)