from pathlib import Path
import json

from src.orchestrator import run_analysis


def test_sample_clean_has_no_local_findings():
    project_path = Path("test_projects/sample_clean").resolve()

    output_dir = run_analysis(
        project_path=str(project_path),
        selected_smells=[
            "pinned-dependency",
            "url-dependency",
            "restrictive-constraint",
            "permissive-constraint",
            "duplicate-versions",
        ],
    )

    findings_path = Path(output_dir) / "findings.json"
    findings = json.loads(findings_path.read_text(encoding="utf-8"))

    assert findings == []