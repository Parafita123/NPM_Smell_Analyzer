from pathlib import Path
import json

from src.orchestrator import run_analysis


def test_sample_installation_scripts_detects_installation_scripts():
    project_path = Path("test_projects/sample_installation_scripts").resolve()

    output_dir = run_analysis(
        project_path=str(project_path),
        selected_smells=["installation-scripts"],
    )

    findings = json.loads((Path(output_dir) / "findings.json").read_text(encoding="utf-8"))

    assert any(f["smell"] == "installation-scripts" for f in findings)