from pathlib import Path
import json

from src.orchestrator import run_analysis


def test_sample_knip_detects_knip_smells():
    project_path = Path("test_projects/sample_knip").resolve()

    output_dir = run_analysis(
        project_path=str(project_path),
        selected_smells=["unused-dependency", "missing-dependency"],
    )

    findings = json.loads((Path(output_dir) / "findings.json").read_text(encoding="utf-8"))

    smell_names = {f["smell"] for f in findings}

    assert "unused-dependency" in smell_names or "missing-dependency" in smell_names