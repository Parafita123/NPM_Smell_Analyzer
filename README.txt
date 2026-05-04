React Smell Analyzer

Minimal CLI prototype to analyze React/npm projects and detect selected supply chain smells.

    Current supported smells
- no-package-lock
- pinned-dependency

    Usage

Analyze all supported smells:

```bash
python main.py --project "C:\path\to\react-project" --all