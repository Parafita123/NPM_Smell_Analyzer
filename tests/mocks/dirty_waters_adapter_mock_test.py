import os
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from src.external_tools.dirty_waters_adapter import run_dirty_waters_check


def _fake_completed_process(returncode=0, stdout="", stderr=""):
    return SimpleNamespace(
        returncode=returncode,
        stdout=stdout,
        stderr=stderr,
    )


def _write_debug_files(base_dir: Path, stdout_text="", stderr_text="", report_text=None):
    debug_dir = base_dir / "dirty_waters_debug"
    debug_dir.mkdir(exist_ok=True)

    (debug_dir / "dirty_waters_stdout.txt").write_text(
        stdout_text,
        encoding="utf-8",
    )
    (debug_dir / "dirty_waters_stderr.txt").write_text(
        stderr_text,
        encoding="utf-8",
    )

    if report_text is not None:
        (debug_dir / "dirty_waters_report.md").write_text(
            report_text,
            encoding="utf-8",
        )


def test_dirty_waters_adapter_returns_error_when_backend_is_disabled(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("GITHUB_API_TOKEN", "fake-token")

    result, errors = run_dirty_waters_check(
        repo_name="owner/repo",
        package_manager="npm",
        check_flags=["--check-deprecated"],
        backend="disabled",
    )

    assert result is None
    assert len(errors) == 1
    assert "Dirty-Waters backend is disabled" in errors[0]


def test_dirty_waters_adapter_returns_error_when_token_is_missing(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("GITHUB_API_TOKEN", raising=False)

    result, errors = run_dirty_waters_check(
        repo_name="owner/repo",
        package_manager="npm",
        check_flags=["--check-deprecated"],
        backend="wsl",
    )

    assert result is None
    assert len(errors) == 1
    assert "GITHUB_API_TOKEN is not set" in errors[0]


@patch("src.external_tools.dirty_waters_adapter.subprocess.run")
def test_dirty_waters_adapter_success_with_report_copied_back(mock_run, monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("GITHUB_API_TOKEN", "fake-token")

    stdout_text = (
        "Table github_urls is up to date\n"
        "Report from static analysis generated at "
        "results/results_2026-05-17-17-23-30/abc123_static_summary.md\n"
    )
    stderr_text = "Analysis completed.\n"
    report_text = "# Dirty-Waters Report\n\nPackages that are deprecated (⚠️⚠️): 1\n"

    def fake_run(*args, **kwargs):
        _write_debug_files(
            base_dir=tmp_path,
            stdout_text=stdout_text,
            stderr_text=stderr_text,
            report_text=report_text,
        )
        return _fake_completed_process(returncode=0)

    mock_run.side_effect = fake_run

    result, errors = run_dirty_waters_check(
        repo_name="owner/repo",
        package_manager="npm",
        check_flags=["--check-deprecated"],
        backend="wsl",
        wsl_distro="Ubuntu",
        dirty_waters_root="/home/testuser/dirty-waters",
    )

    assert errors == []
    assert result is not None
    assert result.report_text == report_text
    assert result.report_path == (
        "/home/testuser/dirty-waters/tool/"
        "results/results_2026-05-17-17-23-30/abc123_static_summary.md"
    )
    assert result.user_report_location == (
        r"\\wsl.localhost\Ubuntu\home\testuser\dirty-waters\tool\results"
        r"\results_2026-05-17-17-23-30\abc123_static_summary.md"
    )
    assert "copied back" in (result.note or "")


@patch("src.external_tools.dirty_waters_adapter.subprocess.run")
def test_dirty_waters_adapter_success_without_report_copy_but_with_report_path(mock_run, monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("GITHUB_API_TOKEN", "fake-token")

    stdout_text = (
        "Table github_urls is up to date\n"
        "Report from static analysis generated at "
        "results/results_2026-05-17-17-30-00/abc123_static_summary.md\n"
    )
    stderr_text = "Analysis completed.\n"

    def fake_run(*args, **kwargs):
        _write_debug_files(
            base_dir=tmp_path,
            stdout_text=stdout_text,
            stderr_text=stderr_text,
            report_text=None,
        )
        return _fake_completed_process(returncode=0)

    mock_run.side_effect = fake_run

    result, errors = run_dirty_waters_check(
        repo_name="owner/repo",
        package_manager="npm",
        check_flags=["--check-source-code"],
        backend="wsl",
        wsl_distro="Ubuntu",
        dirty_waters_root="/home/testuser/dirty-waters",
    )

    assert errors == []
    assert result is not None
    assert result.report_text is None
    assert result.report_path == (
        "/home/testuser/dirty-waters/tool/"
        "results/results_2026-05-17-17-30-00/abc123_static_summary.md"
    )
    assert result.user_report_location == (
        r"\\wsl.localhost\Ubuntu\home\testuser\dirty-waters\tool\results"
        r"\results_2026-05-17-17-30-00\abc123_static_summary.md"
    )
    assert "generated inside WSL" in (result.note or "")


@patch("src.external_tools.dirty_waters_adapter.subprocess.run")
def test_dirty_waters_adapter_returns_error_when_subprocess_fails(mock_run, monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("GITHUB_API_TOKEN", "fake-token")

    def fake_run(*args, **kwargs):
        _write_debug_files(
            base_dir=tmp_path,
            stdout_text="some stdout\n",
            stderr_text="fatal error\n",
            report_text=None,
        )
        return _fake_completed_process(returncode=1)

    mock_run.side_effect = fake_run

    result, errors = run_dirty_waters_check(
        repo_name="owner/repo",
        package_manager="npm",
        check_flags=["--check-deprecated"],
        backend="wsl",
        wsl_distro="Ubuntu",
        dirty_waters_root="/home/testuser/dirty-waters",
    )

    assert result is None
    assert len(errors) == 1
    assert "Dirty-Waters failed in WSL with exit code 1" in errors[0]


@patch("src.external_tools.dirty_waters_adapter.subprocess.run")
def test_dirty_waters_adapter_returns_error_when_report_path_cannot_be_determined(mock_run, monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("GITHUB_API_TOKEN", "fake-token")

    def fake_run(*args, **kwargs):
        _write_debug_files(
            base_dir=tmp_path,
            stdout_text="Analysis completed but no report path here\n",
            stderr_text="",
            report_text=None,
        )
        return _fake_completed_process(returncode=0)

    mock_run.side_effect = fake_run

    result, errors = run_dirty_waters_check(
        repo_name="owner/repo",
        package_manager="npm",
        check_flags=["--check-deprecated"],
        backend="wsl",
        wsl_distro="Ubuntu",
        dirty_waters_root="/home/testuser/dirty-waters",
    )

    assert result is None
    assert len(errors) == 1
    assert "report path could not be determined" in errors[0]