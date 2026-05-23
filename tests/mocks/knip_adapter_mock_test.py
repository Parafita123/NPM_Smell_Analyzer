import subprocess
from types import SimpleNamespace
from unittest.mock import patch

from src.external_tools.knip_adapter import run_knip_dependency_analysis


def _fake_completed_process(returncode=0, stdout="", stderr=""):
    return SimpleNamespace(
        returncode=returncode,
        stdout=stdout,
        stderr=stderr,
    )


@patch("src.external_tools.knip_adapter._find_knip_command")
@patch("src.external_tools.knip_adapter.subprocess.run")
def test_knip_adapter_parses_unused_dependency(mock_run, mock_find_command, tmp_path):
    mock_find_command.return_value = ["npx", "knip"]
    mock_run.return_value = _fake_completed_process(
        returncode=1,
        stdout="""
        {
          "issues": [
            {
              "file": "package.json",
              "dependencies": [
                {
                  "name": "lodash",
                  "line": 5,
                  "col": 6
                }
              ]
            }
          ]
        }
        """,
        stderr="",
    )

    findings, errors = run_knip_dependency_analysis(str(tmp_path))

    assert errors == []
    assert len(findings) == 1
    assert findings[0].smell == "unused-dependency"
    assert findings[0].dependency == "lodash"
    assert findings[0].evidence["file"] == "package.json"
    assert findings[0].evidence["issue_type"] == "dependencies"


@patch("src.external_tools.knip_adapter._find_knip_command")
@patch("src.external_tools.knip_adapter.subprocess.run")
def test_knip_adapter_parses_unused_dev_dependency(mock_run, mock_find_command, tmp_path):
    mock_find_command.return_value = ["npx", "knip"]
    mock_run.return_value = _fake_completed_process(
        returncode=1,
        stdout="""
        {
          "issues": [
            {
              "file": "package.json",
              "devDependencies": [
                {
                  "name": "jest",
                  "line": 12,
                  "col": 4
                }
              ]
            }
          ]
        }
        """,
        stderr="",
    )

    findings, errors = run_knip_dependency_analysis(str(tmp_path))

    assert errors == []
    assert len(findings) == 1
    assert findings[0].smell == "unused-dependency"
    assert findings[0].dependency == "jest"
    assert findings[0].evidence["issue_type"] == "devDependencies"


@patch("src.external_tools.knip_adapter._find_knip_command")
@patch("src.external_tools.knip_adapter.subprocess.run")
def test_knip_adapter_parses_missing_dependency(mock_run, mock_find_command, tmp_path):
    mock_find_command.return_value = ["npx", "knip"]
    mock_run.return_value = _fake_completed_process(
        returncode=1,
        stdout="""
        {
          "issues": [
            {
              "file": "src/index.js",
              "unlisted": [
                {
                  "name": "axios",
                  "line": 1,
                  "col": 19
                }
              ]
            }
          ]
        }
        """,
        stderr="",
    )

    findings, errors = run_knip_dependency_analysis(str(tmp_path))

    assert errors == []
    assert len(findings) == 1
    assert findings[0].smell == "missing-dependency"
    assert findings[0].dependency == "axios"
    assert findings[0].evidence["file"] == "src/index.js"
    assert findings[0].evidence["issue_type"] == "unlisted"


@patch("src.external_tools.knip_adapter._find_knip_command")
@patch("src.external_tools.knip_adapter.subprocess.run")
def test_knip_adapter_returns_no_findings_when_issues_are_empty(mock_run, mock_find_command, tmp_path):
    mock_find_command.return_value = ["npx", "knip"]
    mock_run.return_value = _fake_completed_process(
        returncode=0,
        stdout='{"issues": []}',
        stderr="",
    )

    findings, errors = run_knip_dependency_analysis(str(tmp_path))

    assert errors == []
    assert findings == []


@patch("src.external_tools.knip_adapter._find_knip_command")
def test_knip_adapter_returns_error_when_knip_command_not_found(mock_find_command, tmp_path):
    mock_find_command.return_value = None

    findings, errors = run_knip_dependency_analysis(str(tmp_path))

    assert findings == []
    assert len(errors) == 1
    assert "Knip is not available for this project" in errors[0]


@patch("src.external_tools.knip_adapter._find_knip_command")
@patch("src.external_tools.knip_adapter.subprocess.run")
def test_knip_adapter_returns_error_on_invalid_json(mock_run, mock_find_command, tmp_path):
    mock_find_command.return_value = ["npx", "knip"]
    mock_run.return_value = _fake_completed_process(
        returncode=1,
        stdout="not valid json",
        stderr="",
    )

    findings, errors = run_knip_dependency_analysis(str(tmp_path))

    assert findings == []
    assert len(errors) == 1
    assert "Failed to parse Knip JSON output" in errors[0]


@patch("src.external_tools.knip_adapter._find_knip_command")
@patch("src.external_tools.knip_adapter.subprocess.run")
def test_knip_adapter_returns_error_when_subprocess_fails(mock_run, mock_find_command, tmp_path):
    mock_find_command.return_value = ["npx", "knip"]
    mock_run.side_effect = subprocess.SubprocessError("mocked subprocess failure")

    findings, errors = run_knip_dependency_analysis(str(tmp_path))

    assert findings == []
    assert len(errors) == 1
    assert "Failed to execute Knip" in errors[0]


@patch("src.external_tools.knip_adapter._find_knip_command")
@patch("src.external_tools.knip_adapter.subprocess.run")
def test_knip_adapter_returns_error_for_unexpected_return_code(mock_run, mock_find_command, tmp_path):
    mock_find_command.return_value = ["npx", "knip"]
    mock_run.return_value = _fake_completed_process(
        returncode=2,
        stdout="",
        stderr="some fatal error",
    )

    findings, errors = run_knip_dependency_analysis(str(tmp_path))

    assert findings == []
    assert len(errors) == 1
    assert "Knip returned unexpected exit code 2" in errors[0]