from pathlib import Path
import json

from src.orchestrator import run_analysis


def test_sample_duplicate_versions_detects_duplicate_versions():
    project_path = Path("test_projects/sample_duplicate_versions").resolve()

    output_dir = run_analysis(
        project_path=str(project_path),
        selected_smells=["duplicate-versions"],
    )

    findings = json.loads((Path(output_dir) / "findings.json").read_text(encoding="utf-8"))

    smell_names = [f["smell"] for f in findings]
    assert "duplicate-versions" in smell_names