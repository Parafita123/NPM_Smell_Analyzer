from pathlib import Path
import json

from src.orchestrator import run_analysis


def test_sample_mixed_detects_expected_smells():
    project_path = Path("test_projects/sample_mixed").resolve()

    output_dir = run_analysis(
        project_path=str(project_path),
        selected_smells=[
            "pinned-dependency",
            "url-dependency",
            "restrictive-constraint",
            "permissive-constraint",
        ],
    )

    findings = json.loads((Path(output_dir) / "findings.json").read_text(encoding="utf-8"))

    smell_names = {f["smell"] for f in findings}

    assert "pinned-dependency" in smell_names
    assert "url-dependency" in smell_names