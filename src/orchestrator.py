from src.analyzers.manifest_reader import read_package_json
from src.analyzers.lockfile_reader import read_package_lock_json
from src.models import AnalysisResult
from src.report_writer import write_report
from src.smells.registry import SMELL_REGISTRY


DIRTY_WATERS_SMELLS = {
    "deprecated-dependency",
    "no-source-code-link",
    "no-source-code-sha",
    "depends-on-fork",
    "no-build-attestation",
    "no-invalid-code-signature",
    "aliased-packages",
}

SUPPORTED_SMELLS = set(SMELL_REGISTRY.keys())
DEFAULT_ALL_SMELLS = sorted(SUPPORTED_SMELLS - DIRTY_WATERS_SMELLS)
DIRTY_WATERS_ALL_SMELLS = sorted(DIRTY_WATERS_SMELLS)

PACKAGE_JSON_SMELLS = {
    "pinned-dependency",
    "url-dependency",
    "restrictive-constraint",
    "permissive-constraint",
    "unmaintained-package",
}

PACKAGE_LOCK_SMELLS = {
    "duplicate-versions",
}


def run_analysis(
    project_path: str,
    selected_smells: list[str],
    repo_name: str | None = None,
    dirty_waters_backend: str = "disabled",
    wsl_distro: str = "Ubuntu",
    dirty_waters_root: str = "/home/parafita/dirty-waters",
    unmaintained_threshold_months: int = 24,
) -> str:
    result = AnalysisResult(
        project_path=project_path,
        selected_smells=selected_smells,
    )

    package_json = None
    package_lock = None

    if any(smell in selected_smells for smell in PACKAGE_JSON_SMELLS):
        try:
            package_json = read_package_json(project_path)
        except Exception as exc:
            result.errors.append(str(exc))

    if any(smell in selected_smells for smell in PACKAGE_LOCK_SMELLS):
        try:
            package_lock = read_package_lock_json(project_path)
        except Exception as exc:
            result.errors.append(str(exc))

    context = {
        "project_path": project_path,
        "package_json": package_json,
        "package_lock": package_lock,
        "repo_name": repo_name,
        "dirty_waters_backend": dirty_waters_backend,
        "wsl_distro": wsl_distro,
        "dirty_waters_root": dirty_waters_root,
        "unmaintained_threshold_months": unmaintained_threshold_months,
    }

    for smell in selected_smells:
        detector = SMELL_REGISTRY.get(smell)
        if detector is None:
            result.errors.append(f"Unsupported smell: {smell}")
            continue

        try:
            findings = detector.detect(**context)
            result.findings.extend(findings)
        except Exception as exc:
            result.errors.append(f"{smell}: {exc}")

    output_dir = write_report(result)
    return str(output_dir)