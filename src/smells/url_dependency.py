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


class UrlDependencyDetector(SmellDetector):
    smell_name = "url-dependency"

    def detect(self, **kwargs) -> list[Finding]:
        package_json = kwargs["package_json"]
        findings: list[Finding] = []

        for section in ("dependencies", "devDependencies"):
            deps = package_json.get(section, {})
            if not isinstance(deps, dict):
                continue

            for dep_name, version in deps.items():
                if isinstance(version, str) and version.strip().startswith(URL_PREFIXES):
                    findings.append(
                        Finding(
                            smell=self.smell_name,
                            dependency=dep_name,
                            severity="medium",
                            evidence={
                                "section": section,
                                "declared_version": version,
                            },
                            message=(
                                f"Dependency '{dep_name}' is declared through a URL- or "
                                f"repository-based source ('{version}') in {section}."
                            ),
                        )
                    )

        return findings