from collections import defaultdict
from src.models import Finding
from src.smells.base import SmellDetector


def _derive_package_name(package_path: str) -> str | None:
    if not package_path or package_path == "":
        return None

    marker = "node_modules/"
    if marker not in package_path:
        return None

    tail = package_path.split(marker)[-1]
    parts = tail.split("/")

    if not parts:
        return None

    if parts[0].startswith("@") and len(parts) >= 2:
        return f"{parts[0]}/{parts[1]}"

    return parts[0]


class DuplicateVersionsDetector(SmellDetector):
    smell_name = "duplicate-versions"

    def detect(self, **kwargs) -> list[Finding]:
        package_lock = kwargs["package_lock"]
        findings: list[Finding] = []

        packages = package_lock.get("packages", {})
        if not isinstance(packages, dict):
            return findings

        versions_by_name: dict[str, set[str]] = defaultdict(set)

        for package_path, metadata in packages.items():
            if package_path == "":
                continue
            if not isinstance(metadata, dict):
                continue

            version = metadata.get("version")
            package_name = _derive_package_name(package_path)

            if package_name and isinstance(version, str):
                versions_by_name[package_name].add(version)

        for package_name, versions in versions_by_name.items():
            if len(versions) > 1:
                sorted_versions = sorted(versions)
                findings.append(
                    Finding(
                        smell=self.smell_name,
                        dependency=package_name,
                        severity="low",
                        evidence={
                            "versions": sorted_versions,
                            "version_count": len(sorted_versions),
                        },
                        message=(
                            f"Dependency '{package_name}' appears with multiple "
                            f"resolved versions: {', '.join(sorted_versions)}."
                        ),
                    )
                )

        return findings