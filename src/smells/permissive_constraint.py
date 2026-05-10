from src.models import Finding
from src.smells.base import SmellDetector


URL_PREFIXES = (
    "http://",
    "https://",
    "git+https://",
    "git+ssh://",
    "git://",
    "github:",
    "gitlab:",
    "file:",
    "link:",
)


def _is_permissive_constraint(version: str) -> bool:
    v = version.strip().lower()

    if not v or v.startswith(URL_PREFIXES):
        return False

    if v in {"*", "latest", "x"}:
        return True

    if v.endswith(".x") or v.endswith(".*"):
        return True

    if v.startswith(">=") and "<" not in v:
        return True

    if v.startswith(">") and not v.startswith(">="):
        return True

    return False


class PermissiveConstraintDetector(SmellDetector):
    smell_name = "permissive-constraint"

    def detect(self, **kwargs) -> list[Finding]:
        package_json = kwargs["package_json"]
        findings: list[Finding] = []

        if package_json is None:
            return findings

        for section in ("dependencies", "devDependencies"):
            deps = package_json.get(section, {})
            if not isinstance(deps, dict):
                continue

            for dep_name, version in deps.items():
                if isinstance(version, str) and _is_permissive_constraint(version):
                    findings.append(
                        Finding(
                            smell=self.smell_name,
                            dependency=dep_name,
                            severity="medium",
                            evidence={
                                "section": section,
                                "declared_version": version,
                                "policy": "wildcard, latest tag, x-range, or open-ended lower-bound range",
                            },
                            message=(
                                f"Dependency '{dep_name}' uses a permissive version "
                                f"constraint ('{version}') in {section}."
                            ),
                        )
                    )

        return findings