import argparse

from src.config import load_config
from src.orchestrator import (
    SUPPORTED_SMELLS,
    DEFAULT_ALL_SMELLS,
    DIRTY_WATERS_ALL_SMELLS,
    DIRTY_WATERS_SMELLS,
    run_analysis,
)


def _pick(cli_value, config_value, default_value=None):
    if cli_value is not None:
        return cli_value
    if config_value is not None:
        return config_value
    return default_value


def _deduplicate_preserve_order(items: list[str]) -> list[str]:
    seen = set()
    result = []

    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)

    return result


def _resolve_smells(args, config):
    selected_modes = sum(
        [
            bool(args.all),
            bool(args.dirty_waters_all),
            bool(args.smell),
        ]
    )

    if selected_modes > 1:
        raise RuntimeError(
            "Use only one of: --all, --dirty-waters-all, or --smell."
        )

    if args.all:
        return DEFAULT_ALL_SMELLS

    if args.dirty_waters_all:
        return DIRTY_WATERS_ALL_SMELLS

    if args.smell:
        for smell in args.smell:
            if smell not in SUPPORTED_SMELLS:
                raise RuntimeError(
                    f"Unsupported smell requested on the command line: '{smell}'. "
                    f"Supported smells: {sorted(SUPPORTED_SMELLS)}"
                )
        return _deduplicate_preserve_order(args.smell)

    config_smells = config.get("smells")

    if config_smells is None:
        raise RuntimeError(
            "No smells were selected. "
            "Use --all, --dirty-waters-all, --smell, or define 'smells' in a configuration file."
        )

    if not isinstance(config_smells, list) or not config_smells:
        raise RuntimeError(
            "The configuration key 'smells' must be a non-empty list."
        )

    if config_smells == ["all"]:
        return DEFAULT_ALL_SMELLS

    if config_smells == ["dirty-waters-all"]:
        return DIRTY_WATERS_ALL_SMELLS

    for smell in config_smells:
        if smell not in SUPPORTED_SMELLS:
            raise RuntimeError(
                f"Unsupported smell in configuration: '{smell}'. "
                f"Supported smells: {sorted(SUPPORTED_SMELLS)}"
            )

    return _deduplicate_preserve_order(config_smells)


def run() -> None:
    parser = argparse.ArgumentParser(
        description="Analyze a npm project for selected supply chain smells."
    )

    parser.add_argument(
        "--project",
        required=True,
        help="Path to the npm project.",
    )
    parser.add_argument(
        "--config",
        help="Optional path to a configuration file.",
    )

    parser.add_argument(
        "--all",
        action="store_true",
        help="Run all default local and Knip-based smells.",
    )
    parser.add_argument(
        "--dirty-waters-all",
        action="store_true",
        help="Run all Dirty-Waters-based smells.",
    )
    parser.add_argument(
        "--smell",
        action="append",
        help="Run one or more specific smells. Repeat the argument to add more than one.",
    )

    parser.add_argument(
        "--repo",
        default=None,
        help="GitHub repository identifier, for example owner/repo.",
    )
    parser.add_argument(
        "--dirty-waters-backend",
        choices=["disabled", "wsl", "native", "auto"],
        default=None,
        help="How to run Dirty-Waters.",
    )
    parser.add_argument(
        "--wsl-distro",
        default=None,
        help="WSL distro name.",
    )
    parser.add_argument(
        "--dirty-waters-root",
        default=None,
        help="Path to the Dirty-Waters installation.",
    )
    parser.add_argument(
        "--unmaintained-threshold-months",
        type=int,
        default=None,
        help="Threshold in months used by the unmaintained-package smell.",
    )

    args = parser.parse_args()

    try:
        config = load_config(args.project, args.config)

        selected_smells = _resolve_smells(args, config)

        repo_name = _pick(args.repo, config.get("repo"))
        dirty_waters_backend = _pick(
            args.dirty_waters_backend,
            config.get("dirty_waters_backend"),
            "disabled",
        )
        wsl_distro = _pick(
            args.wsl_distro,
            config.get("wsl_distro"),
            "Ubuntu",
        )
        dirty_waters_root = _pick(
            args.dirty_waters_root,
            config.get("dirty_waters_root"),
            "/home/parafita/dirty-waters",
        )
        unmaintained_threshold_months = _pick(
            args.unmaintained_threshold_months,
            config.get("unmaintained_threshold_months"),
            24,
        )

        if unmaintained_threshold_months <= 0:
            raise RuntimeError(
                "The unmaintained-package threshold must be a positive integer."
            )

        requires_dirty_waters = any(
            smell in DIRTY_WATERS_SMELLS for smell in selected_smells
        )

        if requires_dirty_waters and not repo_name:
            raise RuntimeError(
                "Dirty-Waters-based smells require a GitHub repository identifier. "
                "Provide it with --repo or in the configuration file."
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

    except RuntimeError as exc:
        parser.error(str(exc))
        return

    print("Analysis completed.")
    print(f"Output directory: {output_dir}")
    print(f"Executed smells: {', '.join(selected_smells)}")