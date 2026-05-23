import os
import re
import shlex
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path


@dataclass
class DirtyWatersResult:
    stdout: str
    report_path: str | None
    report_text: str | None
    user_report_location: str | None = None
    note: str | None = None


def _resolve_backend(backend: str) -> str:
    if backend == "auto":
        return "wsl" if os.name == "nt" else "native"
    return backend


def _windows_to_wsl_path(path: str) -> str:
    path = str(Path(path).resolve())
    drive = path[0].lower()
    rest = path[2:].replace("\\", "/")
    return f"/mnt/{drive}{rest}"


def _extract_report_path(stdout_text: str) -> str | None:
    match = re.search(
        r"Report from static analysis generated at (.+)",
        stdout_text,
    )
    if not match:
        return None
    return match.group(1).strip()


def _linux_path_to_wsl_unc(linux_path: str, distro: str) -> str:
    linux_path = linux_path.strip().replace("/", "\\")
    if not linux_path.startswith("\\"):
        linux_path = "\\" + linux_path
    return f"\\\\wsl.localhost\\{distro}{linux_path}"


def _resolve_absolute_report_path(
    relative_report_path: str,
    dirty_waters_root: str,
) -> str:
    relative_report_path = relative_report_path.strip()

    if relative_report_path.startswith("/"):
        return relative_report_path

    dirty_waters_root = dirty_waters_root.rstrip("/")
    return f"{dirty_waters_root}/tool/{relative_report_path}"


def _read_text_if_exists(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def _find_native_python(dirty_waters_root: str) -> str | None:
    root = Path(dirty_waters_root)

    candidates = [
        root / "venv" / "bin" / "python",
        root / "venv" / "Scripts" / "python.exe",
    ]

    for candidate in candidates:
        if candidate.exists():
            return str(candidate)

    return shutil.which("python3") or shutil.which("python")


def _run_dirty_waters_wsl(
    repo_name: str,
    package_manager: str,
    check_flags: list[str],
    github_token: str,
    wsl_distro: str,
    dirty_waters_root: str,
    windows_stdout: Path,
    windows_stderr: Path,
    windows_report: Path,
) -> tuple[int | None, str | None]:
    repo_name_q = shlex.quote(repo_name)
    package_manager_q = shlex.quote(package_manager)
    dirty_waters_root_q = shlex.quote(dirty_waters_root)
    flags_q = " ".join(shlex.quote(flag) for flag in check_flags)

    wsl_stdout = _windows_to_wsl_path(str(windows_stdout))
    wsl_stderr = _windows_to_wsl_path(str(windows_stderr))
    wsl_report = _windows_to_wsl_path(str(windows_report))

    shell_script = f"""
set -o pipefail
export GITHUB_API_TOKEN={shlex.quote(github_token)}
cd {dirty_waters_root_q}/tool || exit 2
source ../venv/bin/activate || exit 3

python main.py -p {repo_name_q} -pm {package_manager_q} --gradual-report false --debug {flags_q} > {shlex.quote(wsl_stdout)} 2> {shlex.quote(wsl_stderr)}
cmd_status=$?

report_path=$(grep 'Report from static analysis generated at ' {shlex.quote(wsl_stdout)} | tail -n 1 | sed 's/^Report from static analysis generated at //')

if [ -n "$report_path" ]; then
  abs_report_path="{dirty_waters_root}/tool/$report_path"
  if [ -f "$abs_report_path" ]; then
    cp "$abs_report_path" {shlex.quote(wsl_report)} 2>/dev/null || true
  fi
fi

exit $cmd_status
"""

    try:
        result = subprocess.run(
            ["wsl", "-d", wsl_distro, "bash", "-lc", shell_script],
            capture_output=True,
            text=True,
            check=False,
        )
    except Exception as exc:
        return None, f"Failed to execute Dirty-Waters through WSL: {exc}"

    return result.returncode, None


def _run_dirty_waters_native(
    repo_name: str,
    package_manager: str,
    check_flags: list[str],
    github_token: str,
    dirty_waters_root: str,
    windows_stdout: Path,
    windows_stderr: Path,
) -> tuple[int | None, str | None]:
    tool_dir = Path(dirty_waters_root) / "tool"
    if not tool_dir.exists():
        return None, f"Dirty-Waters tool directory not found: '{tool_dir}'."

    python_cmd = _find_native_python(dirty_waters_root)
    if not python_cmd:
        return None, "Could not find a Python interpreter for native Dirty-Waters execution."

    full_cmd = [
        python_cmd,
        "main.py",
        "-p",
        repo_name,
        "-pm",
        package_manager,
        "--gradual-report",
        "false",
        "--debug",
        *check_flags,
    ]

    env = os.environ.copy()
    env["GITHUB_API_TOKEN"] = github_token

    try:
        result = subprocess.run(
            full_cmd,
            cwd=tool_dir,
            capture_output=True,
            text=True,
            check=False,
            env=env,
        )
    except Exception as exc:
        return None, f"Failed to execute Dirty-Waters in native mode: {exc}"

    windows_stdout.write_text(result.stdout or "", encoding="utf-8")
    windows_stderr.write_text(result.stderr or "", encoding="utf-8")

    return result.returncode, None


def run_dirty_waters_check(
    repo_name: str,
    package_manager: str,
    check_flags: list[str],
    backend: str = "disabled",
    wsl_distro: str = "Ubuntu",
    dirty_waters_root: str = "/home/parafita/dirty-waters",
) -> tuple[DirtyWatersResult | None, list[str]]:
    errors: list[str] = []

    backend = _resolve_backend(backend)

    if backend == "disabled":
        errors.append(
            "Dirty-Waters backend is disabled. "
            "Use 'wsl', 'native', or 'auto' to enable Dirty-Waters-based analysis."
        )
        return None, errors

    if backend not in {"wsl", "native"}:
        errors.append(
            f"Unsupported Dirty-Waters backend: '{backend}'. "
            "Supported values are: disabled, wsl, native, auto."
        )
        return None, errors

    github_token = os.getenv("GITHUB_API_TOKEN", "").strip()
    if not github_token:
        errors.append(
            "GITHUB_API_TOKEN is not set. Dirty-Waters requires a GitHub token in the environment."
        )
        return None, errors

    windows_debug_dir = Path.cwd() / "dirty_waters_debug"
    windows_debug_dir.mkdir(exist_ok=True)

    windows_stdout = windows_debug_dir / "dirty_waters_stdout.txt"
    windows_stderr = windows_debug_dir / "dirty_waters_stderr.txt"
    windows_report = windows_debug_dir / "dirty_waters_report.md"

    if backend == "wsl":
        returncode, execution_error = _run_dirty_waters_wsl(
            repo_name=repo_name,
            package_manager=package_manager,
            check_flags=check_flags,
            github_token=github_token,
            wsl_distro=wsl_distro,
            dirty_waters_root=dirty_waters_root,
            windows_stdout=windows_stdout,
            windows_stderr=windows_stderr,
            windows_report=windows_report,
        )
    else:
        returncode, execution_error = _run_dirty_waters_native(
            repo_name=repo_name,
            package_manager=package_manager,
            check_flags=check_flags,
            github_token=github_token,
            dirty_waters_root=dirty_waters_root,
            windows_stdout=windows_stdout,
            windows_stderr=windows_stderr,
        )

    if execution_error:
        errors.append(execution_error)
        return None, errors

    stdout_text = _read_text_if_exists(windows_stdout)
    stderr_text = _read_text_if_exists(windows_stderr)
    copied_report_text = _read_text_if_exists(windows_report) or None

    if returncode != 0:
        if backend == "wsl":
            errors.append(
                f"Dirty-Waters failed in WSL with exit code {returncode}. "
                f"stdout: {stdout_text[-2000:] if stdout_text else 'empty'} | "
                f"stderr: {stderr_text[-2000:] if stderr_text else 'empty'}"
            )
        else:
            errors.append(
                f"Dirty-Waters failed in native mode with exit code {returncode}. "
                f"stdout: {stdout_text[-2000:] if stdout_text else 'empty'} | "
                f"stderr: {stderr_text[-2000:] if stderr_text else 'empty'}"
            )
        return None, errors

    relative_report_path = _extract_report_path(stdout_text)
    absolute_linux_report_path = None
    user_report_location = None
    note = None

    if relative_report_path:
        absolute_linux_report_path = _resolve_absolute_report_path(
            relative_report_path,
            dirty_waters_root,
        )

        if backend == "wsl":
            user_report_location = _linux_path_to_wsl_unc(
                absolute_linux_report_path,
                wsl_distro,
            )
        else:
            user_report_location = absolute_linux_report_path

    if backend == "native" and absolute_linux_report_path and not copied_report_text:
        report_file = Path(absolute_linux_report_path)
        if report_file.exists():
            copied_report_text = report_file.read_text(encoding="utf-8", errors="replace")

    if copied_report_text:
        if backend == "wsl":
            note = (
                "Dirty-Waters analysis completed successfully and the report was copied back "
                "to the local debug folder."
            )
        else:
            note = (
                "Dirty-Waters analysis completed successfully and the report was read directly "
                "from the native filesystem."
            )

        return DirtyWatersResult(
            stdout=stdout_text,
            report_path=absolute_linux_report_path,
            report_text=copied_report_text,
            user_report_location=user_report_location,
            note=note,
        ), errors

    if absolute_linux_report_path:
        if backend == "wsl":
            note = (
                "Dirty-Waters analysis completed successfully. "
                "The report was generated inside WSL but was not copied back to the local debug folder. "
                f"Open it here: {user_report_location}"
            )
        else:
            note = (
                "Dirty-Waters analysis completed successfully. "
                f"The report is available here: {user_report_location}"
            )

        return DirtyWatersResult(
            stdout=stdout_text,
            report_path=absolute_linux_report_path,
            report_text=None,
            user_report_location=user_report_location,
            note=note,
        ), errors

    errors.append(
        "Dirty-Waters execution succeeded, but the report path could not be determined from stdout. "
        f"Check: {windows_debug_dir}"
    )
    return None, errors