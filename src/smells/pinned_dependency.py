import re
from src.models import Finding
from src.smells.base import SmellDetector


EXACT_VERSION_PATTERN = re.compile(r"^\d+\.\d+\.\d+$")


class PinnedDependencyDetector(SmellDetector):
    smell_name = "pinned-dependency"

    def detect(self, **kwargs) -> list[Finding]:
        package_json = kwargs["package_json"]
        findings: list[Finding] = []

        for section in ("dependencies", "devDependencies"):
            deps = package_json.get(section, {})
            if not isinstance(deps, dict):
                continue

            for dep_name, version in deps.items():
                if isinstance(version, str) and EXACT_VERSION_PATTERN.fullmatch(version.strip()):
                    findings.append(
                        Finding(
                            smell=self.smell_name,
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