from pathlib import Path
from src.models import Finding
from src.smells.base import SmellDetector


class NoPackageLockDetector(SmellDetector):
    smell_name = "no-package-lock"

    def detect(self, **kwargs) -> list[Finding]:
        project_path = kwargs["project_path"]
        package_lock_path = Path(project_path) / "package-lock.json"

        if package_lock_path.exists():
            return []

        return [
            Finding(
                smell=self.smell_name,
                dependency=None,
                severity="medium",
                evidence={"missing_file": "package-lock.json"},
                message="The project does not contain a package-lock.json file.",
            )
        ]