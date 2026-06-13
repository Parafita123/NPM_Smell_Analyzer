import json
from datetime import datetime
from pathlib import Path

from src.models import AnalysisResult


def write_report(result: AnalysisResult) -> Path:
    # Include microseconds to avoid collisions between runs started
    # during the same second.
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    output_dir = Path("outputs") / f"run_{timestamp}"
    output_dir.mkdir(parents=True, exist_ok=False)

    with (output_dir / "findings.json").open("w", encoding="utf-8") as f:
        json.dump(
            [finding.to_dict() for finding in result.findings],
            f,
            indent=2,
        )

    with (output_dir / "errors.json").open("w", encoding="utf-8") as f:
        json.dump(result.errors, f, indent=2)

    with (output_dir / "report.txt").open("w", encoding="utf-8") as f:
        f.write("NPM Smell Analyzer Report\n")
        f.write("=" * 30 + "\n\n")
        f.write(f"Project: {result.project_path}\n")
        f.write(f"Selected smells: {', '.join(result.selected_smells)}\n")
        f.write(f"Total findings: {len(result.findings)}\n")
        f.write(f"Total errors: {len(result.errors)}\n\n")

        if result.findings:
            f.write("Findings:\n")
            for idx, finding in enumerate(result.findings, start=1):
                f.write(f"{idx}. [{finding.smell}] {finding.message}\n")
        else:
            f.write("No findings detected.\n")

        if result.errors:
            f.write("\nErrors:\n")
            for error in result.errors:
                f.write(f"- {error}\n")

    return output_dir
