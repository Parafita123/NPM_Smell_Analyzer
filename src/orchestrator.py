from src.analyzers.manifest_reader import read_package_json
from src.analyzers.lockfile_reader import read_package_lock_json
from src.models import AnalysisResult
from src.report_writer import write_report
from src.smells.registry import SMELL_REGISTRY


SUPPORTED_SMELLS = set(SMELL_REGISTRY.keys())


PACKAGE_JSON_SMELLS = {
    "pinned-dependency",
    "url-dependency",
    "restrictive-constraint",
    "permissive-constraint",
}

PACKAGE_LOCK_SMELLS = {
    "duplicate-versions",
}


def run_analysis(project_path: str, selected_smells: list[str]) -> str:
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