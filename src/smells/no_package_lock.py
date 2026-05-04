from pathlib import Path
from src.models import Finding


def detect_no_package_lock(project_path: str) -> list[Finding]:
    package_lock_path = Path(project_path) / "package-lock.json"

    if package_lock_path.exists():
        return []

    return [
        Finding(
            smell="no-package-lock",
            dependency=None,
            severity="medium",
            evidence={"missing_file": "package-lock.json"},
            message="The project does not contain a package-lock.json file.",
        )
    ]