import re
from src.models import Finding


EXACT_VERSION_PATTERN = re.compile(r"^\d+\.\d+\.\d+$")


def _is_pinned(version: str) -> bool:
    return bool(EXACT_VERSION_PATTERN.fullmatch(version.strip()))


def detect_pinned_dependencies(package_json: dict) -> list[Finding]:
    findings: list[Finding] = []

    for section in ("dependencies", "devDependencies"):
        deps = package_json.get(section, {})
        if not isinstance(deps, dict):
            continue

        for dep_name, version in deps.items():
            if isinstance(version, str) and _is_pinned(version):
                findings.append(
                    Finding(
                        smell="pinned-dependency",
                        dependency=dep_name,
                        severity="low",
                        evidence={
                            "section": section,
                            "declared_version": version,
                        },
                        message=(
                            f"Dependency '{dep_name}' is pinned to the exact "
                            f"version '{version}' in {section}."
                        ),
                    )
                )

    return findings