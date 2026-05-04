import argparse
from src.orchestrator import SUPPORTED_SMELLS, run_analysis


def run() -> None:
    parser = argparse.ArgumentParser(
        description="Analyze a React/npm project for selected supply chain smells."
    )
    parser.add_argument(
        "--project",
        required=True,
        help="Path to the React/npm project.",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Run all supported smells.",
    )
    parser.add_argument(
        "--smell",
        action="append",
        help="Run one or more specific smells. Repeat the argument to add more than one.",
    )

    args = parser.parse_args()

    if not args.all and not args.smell:
        parser.error("Use --all or at least one --smell.")

    if args.all:
        selected_smells = sorted(SUPPORTED_SMELLS)
    else:
        selected_smells = []
        for smell in args.smell:
            if smell not in SUPPORTED_SMELLS:
                parser.error(
                    f"Unsupported smell: {smell}. Supported smells: {sorted(SUPPORTED_SMELLS)}"
                )
            selected_smells.append(smell)

    output_dir = run_analysis(args.project, selected_smells)

    print("Analysis completed.")
    print(f"Output directory: {output_dir}")
    print(f"Executed smells: {', '.join(selected_smells)}")