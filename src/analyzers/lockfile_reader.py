import json
from pathlib import Path
from typing import Any, Dict


def read_package_lock_json(project_path: str) -> Dict[str, Any]:
    package_lock_path = Path(project_path) / "package-lock.json"

    if not package_lock_path.exists():
        raise FileNotFoundError(f"package-lock.json not found in: {project_path}")

    with package_lock_path.open("r", encoding="utf-8") as f:
        return json.load(f)