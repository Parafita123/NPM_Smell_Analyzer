import re
from src.models import Finding
from src.smells.base import SmellDetector


EXACT_VERSION_PATTERN = re.compile(r"^\d+\.\d+\.\d+$")
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


def _is_restrictive_constraint(version: str) -> bool:
    v = version.strip()

    if not v or v.startswith(URL_PREFIXES):
        return False

    # exact versions are already handled by pinned-dependency
    if EXACT_VERSION_PATTERN.fullmatch(v):
        return False

    if v.startswith("~"):
        return True

    if "<" in v:
        return True

    if " - " in v:
        return True

    if v.startswith("="):
        return True

    return False


class RestrictiveConstraintDetector(SmellDetector):
    smell_name = "restrictive-constraint"

    def detect(self, **kwargs) -> list[Finding]:
        package_json = kwargs["package_json"]
        findings: list[Finding] = []

        for section in ("dependencies", "devDependencies"):
            deps = package_json.get(section, {})
            if not isinstance(deps, dict):
                continue

            for dep_name, version in deps.items():
                if isinstance(version, str) and _is_restrictive_constraint(version):
                    findings.append(
                        Finding(
                            smell=self.smell_name,
                            dependency=dep_name,
                            severity="low",
                            evidence={
                                "section": section,
                                "declared_version": version,
                                "policy": "tilde, upper-bounded range, hyphen range, or exact-bound declaration",
                            },
                            message=(
                                f"Dependency '{dep_name}' uses a restrictive version "
                                f"constraint ('{version}') in {section}."
                            ),
                        )
                    )

        return findings