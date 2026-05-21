import argparse

from src.config import load_config
from src.orchestrator import (
    SUPPORTED_SMELLS,
    DEFAULT_ALL_SMELLS,
    DIRTY_WATERS_ALL_SMELLS,
    run_analysis,
)


def _pick(cli_value, config_value, default_value=None):
    if cli_value is not None:
        return cli_value
    if config_value is not None:
        return config_value
    return default_value


def _resolve_smells(args, config):
    selected_modes = sum(
        [
            bool(args.all),
            bool(args.dirty_waters_all),
            bool(args.smell),
        ]
    )

    if selected_modes > 1:
        raise RuntimeError("Use only one of: --all, --dirty-waters-all, or --smell.")

    if args.all:
        return DEFAULT_ALL_SMELLS

    if args.dirty_waters_all:
        return DIRTY_WATERS_ALL_SMELLS

    if args.smell:
        return args.smell

    config_smells = config.get("smells")

    if not config_smells:
        raise RuntimeError("Use --all, --dirty-waters-all, --smell, or define 'smells' in .smellrc.json.")

    if config_smells == ["all"]:
        return DEFAULT_ALL_SMELLS

    if config_smells == ["dirty-waters-all"]:
        return DIRTY_WATERS_ALL_SMELLS

    for smell in config_smells:
        if smell not in SUPPORTED_SMELLS:
            raise RuntimeError(f"Unsupported smell in config: {smell}")

    return config_smells


def run() -> None:
    parser = argparse.ArgumentParser(
        description="Analyze a React/npm project for selected supply chain smells."
    )

    parser.add_argument("--project", required=True, help="Path to the React/npm project.")
    parser.add_argument("--config", help="Optional path to a configuration file.")

    parser.add_argument("--all", action="store_true", help="Run all default local/fast smells.")
    parser.add_argument("--dirty-waters-all", action="store_true", help="Run all Dirty-Waters-based smells.")
    parser.add_argument("--smell", action="append", help="Run one or more specific smells.")

    parser.add_argument("--repo", default=None, help="GitHub repository identifier, e.g. owner/repo")
    parser.add_argument(
        "--dirty-waters-backend",
        choices=["disabled", "wsl", "native", "auto"],
        default=None,
        help="How to run Dirty-Waters.",
    )
    parser.add_argument("--wsl-distro", default=None, help="WSL distro name.")
    parser.add_argument("--dirty-waters-root", default=None, help="Path to Dirty-Waters inside WSL.")
    parser.add_argument("--unmaintained-threshold-months", type=int, default=None)

    args = parser.parse_args()

    config = load_config(args.project, args.config)

    selected_smells = _resolve_smells(args, config)

    repo_name = _pick(args.repo, config.get("repo"))
    dirty_waters_backend = _pick(args.dirty_waters_backend, config.get("dirty_waters_backend"), "disabled")
    wsl_distro = _pick(args.wsl_distro, config.get("wsl_distro"), "Ubuntu")
    dirty_waters_root = _pick(args.dirty_waters_root, config.get("dirty_waters_root"), "/home/parafita/dirty-waters")
    unmaintained_threshold_months = _pick(
        args.unmaintained_threshold_months,
        config.get("unmaintained_threshold_months"),
        24,
    )

    output_dir = run_analysis(
        project_path=args.project,
        selected_smells=selected_smells,
        repo_name=repo_name,
        dirty_waters_backend=dirty_waters_backend,
        wsl_distro=wsl_distro,
        dirty_waters_root=dirty_waters_root,
        unmaintained_threshold_months=unmaintained_threshold_months,
    )

    print("Analysis completed.")
    print(f"Output directory: {output_dir}")
    print(f"Executed smells: {', '.join(selected_smells)}")