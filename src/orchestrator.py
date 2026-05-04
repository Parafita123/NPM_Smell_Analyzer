from src.analyzers.manifest_reader import read_package_json
from src.models import AnalysisResult
from src.report_writer import write_report
from src.smells.no_package_lock import detect_no_package_lock
from src.smells.pinned_dependency import detect_pinned_dependencies


SUPPORTED_SMELLS = {
    "no-package-lock",
    "pinned-dependency",
}


def run_analysis(project_path: str, selected_smells: list[str]) -> str:
    result = AnalysisResult(
        project_path=project_path,
        selected_smells=selected_smells,
    )

    package_json = None

    if "pinned-dependency" in selected_smells:
        try:
            package_json = read_package_json(project_path)
        except Exception as exc:
            result.errors.append(str(exc))

    if "no-package-lock" in selected_smells:
        result.findings.extend(detect_no_package_lock(project_path))

    if "pinned-dependency" in selected_smells and package_json is not None:
        result.findings.extend(detect_pinned_dependencies(package_json))

    output_dir = write_report(result)
    return str(output_dir)