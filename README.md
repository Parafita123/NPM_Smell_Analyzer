React Smell Analyzer

Minimal CLI prototype to analyze React/npm projects and detect selected supply chain smells.

    Current supported smells
- no-package-lock
- pinned-dependency

    Usage

Analyze all supported smells:

```bash
react-smell-analyzer --project "C:\path\to\react-project" --all


## Test Projects

The repository includes small sample projects under `test_projects/` to validate the currently supported smells and demonstrate expected outputs.