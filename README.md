# NPM Smell Analyzer

NPM Smell Analyzer is a command-line tool for detecting selected software supply chain smells and dependency-related risk indicators in npm projects.

The current prototype combines:

* native local analysis of npm project files;
* dependency usage analysis through Knip;
* selected repository-level checks through Dirty-Waters;
* structured output artifacts for findings and execution errors.

The goal of the tool is not to prove that a dependency is malicious or exploitable. Instead, it highlights dependency-related patterns that may deserve manual inspection by developers.

---

## Current Scope

The current prototype targets projects in the npm ecosystem and analyzes information derived from:

* `package.json`;
* `package-lock.json`;
* locally installed dependencies in `node_modules` for selected smells;
* source code usage analysis through Knip;
* repository-level metadata through Dirty-Waters.

The prototype is focused on lightweight, developer-oriented analysis and reporting.

It does **not**:

* execute dependency code during native analysis;
* confirm malicious intent;
* prove exploitability;
* fully replace specialized vulnerability scanners or ecosystem tools.

Instead, it reports software supply chain smells and risk indicators that may support earlier inspection and more informed maintenance decisions.

---

## Supported Smells

The current prototype supports 17 smells, organized into three detection groups.

### Native local smells

These smells are detected directly by the tool through local parsing, rule-based analysis, or lightweight metadata inspection:

* `no-package-lock`
* `pinned-dependency`
* `url-dependency`
* `restrictive-constraint`
* `permissive-constraint`
* `duplicate-versions`
* `installation-scripts`
* `unmaintained-package`

### Knip-based smells

These smells are detected through integration with [Knip](https://knip.dev/):

* `unused-dependency`
* `missing-dependency`

### Dirty-Waters-based smells

These smells are detected through integration with [Dirty-Waters](https://github.com/chains-project/dirty-waters/):

* `deprecated-dependency`
* `no-source-code-link`
* `no-source-code-sha`
* `depends-on-fork`
* `no-build-attestation`
* `no-invalid-code-signature`
* `aliased-packages`

> **Note:** Dirty-Waters-based smells are external, slower, GitHub-dependent, and WSL/Ubuntu-oriented in the tested Windows environment. They must be executed explicitly and are not part of the default `--all` workflow.

---

## Installation

Clone the repository and install the tool in editable mode:

```bash
git clone https://github.com/Parafita123/NPM_Smell_Analyzer.git
cd NPM_Smell_Analyzer
python -m pip install -e .
```

After installation, the CLI should be available as:

```bash
npm-smell-analyzer --help
```

---

## Core Requirements

The default local analysis requires:

* Python 3.10 or higher;
* an npm-based project to analyze.

For Knip-based smells, the target project must be able to run Knip. In practice, this usually means that Knip should be available locally in the analyzed project or executable through `npx`.

Example installation inside the target npm project:

```bash
npm install -D knip typescript @types/node
```

Dirty-Waters-based smells require additional setup, described in the [Dirty-Waters Integration](#dirty-waters-integration-wslubuntu) section.

---

## Analysis Modes

The tool supports three main execution modes.

### 1. Default local and Knip-based analysis

Runs the default local and Knip-based smells:

```bash
npm-smell-analyzer --project "C:\path\to\npm-project" --all
```

The `--all` mode includes:

* native local smells;
* Knip-based dependency usage smells.

It does **not** include Dirty-Waters-based smells.

### 2. Dirty-Waters full analysis

Runs all Dirty-Waters-based smells:

```bash
npm-smell-analyzer --project "C:\path\to\npm-project" --repo owner/repo --dirty-waters-backend wsl --wsl-distro Ubuntu --dirty-waters-root /home/<your-user>/dirty-waters --dirty-waters-all
```

### 3. Specific smell analysis

Runs one or more explicitly selected smells:

```bash
npm-smell-analyzer --project "C:\path\to\npm-project" --smell duplicate-versions
```

Multiple smells can be selected by repeating `--smell`:

```bash
npm-smell-analyzer --project "C:\path\to\npm-project" --smell pinned-dependency --smell url-dependency
```

Example with a Dirty-Waters-based smell:

```bash
npm-smell-analyzer --project "C:\path\to\npm-project" --repo owner/repo --dirty-waters-backend wsl --wsl-distro Ubuntu --dirty-waters-root /home/<your-user>/dirty-waters --smell deprecated-dependency
```

---

## Output Artifacts

Each analysis run generates an output directory under:

```text
outputs/run_<timestamp>/
```

The generated artifacts are:

* `findings.json` — structured list of detected findings;
* `errors.json` — structured list of execution errors or warnings;
* `report.txt` — human-readable report for direct inspection.

The text report summarizes:

* analyzed project path;
* selected smells;
* total number of findings;
* total number of errors;
* detected findings;
* execution errors, when applicable.

---

## Important Notes About Selected Smells

### `installation-scripts`

This smell requires `node_modules` to be installed locally, because it inspects dependency-level `package.json` files inside the installed dependency tree.

It detects lifecycle scripts such as:

* `preinstall`
* `install`
* `postinstall`

### `unmaintained-package`

This smell is heuristic-based. In the current prototype, it uses npm registry metadata and flags packages whose last registry modification is older than a configurable threshold.

A flagged package is not necessarily abandoned. It should be interpreted as a risk indicator that may deserve manual inspection.

The default threshold is 24 months.

---

## Dirty-Waters Integration: WSL/Ubuntu

NPM Smell Analyzer supports a subset of smells through the external tool [Dirty-Waters](https://github.com/chains-project/dirty-waters/).

Dirty-Waters-based smells are different from the local smells implemented directly in this project:

* they are slower to execute;
* they require a GitHub repository identifier in the form `owner/repo`;
* they require a GitHub API token;
* in the tested Windows environment, they were validated through WSL/Ubuntu.

Because of these requirements, Dirty-Waters-based smells are not included in the default `--all` workflow and should be executed explicitly.

### Requirements

To use Dirty-Waters-based smells in the tested Windows setup, the following requirements apply:

* Windows with WSL installed;
* an Ubuntu distribution inside WSL;
* a local clone of Dirty-Waters inside Ubuntu;
* a valid GitHub Personal Access Token;
* a project hosted on GitHub.

### 1. Install WSL

Open PowerShell as Administrator and run:

```powershell
wsl --install -d Ubuntu
```

Restart the computer if requested.

After restarting, open Ubuntu and complete the initial setup by creating:

* a Linux username;
* a Linux password.

### 2. Prepare Ubuntu

Inside Ubuntu, install the required tools:

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip git nodejs npm curl
```

### 3. Create a GitHub token

Create a fine-grained personal access token in GitHub with:

* resource owner: your GitHub account;
* repository access: only selected repositories;
* selected repository: the repository you want to analyze;
* repository permissions:

  * Metadata: read-only;
  * Contents: read-only.

This token is required by Dirty-Waters to access repository metadata.

### 4. Configure the GitHub token

When running NPM Smell Analyzer from CMD or PowerShell, define the token in the same Windows terminal:

```cmd
set GITHUB_API_TOKEN=YOUR_TOKEN_HERE
```

To make it persistent for future terminals:

```cmd
setx GITHUB_API_TOKEN "YOUR_TOKEN_HERE"
```

For standalone Dirty-Waters usage inside Ubuntu/WSL:

```bash
export GITHUB_API_TOKEN='YOUR_TOKEN_HERE'
```

To make it persistent inside Ubuntu:

```bash
echo 'export GITHUB_API_TOKEN="YOUR_TOKEN_HERE"' >> ~/.bashrc
source ~/.bashrc
```

### 5. Clone and install Dirty-Waters inside Ubuntu

Inside Ubuntu:

```bash
cd ~
git clone https://github.com/chains-project/dirty-waters.git
cd dirty-waters
python3 -m venv venv
source venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .
```

At this point, Dirty-Waters should be available inside WSL.

### 6. Validate standalone Dirty-Waters execution

To validate that Dirty-Waters works correctly in Ubuntu:

```bash
cd ~/dirty-waters/tool
python main.py -p OWNER/REPOSITORY -pm npm --gradual-report false --check-deprecated --debug
```

Example:

```bash
cd ~/dirty-waters/tool
python main.py -p Parafita123/DSSMV_ProjectReact_1231283_1231051 -pm npm --gradual-report false --check-deprecated --debug
```

Another example for source-code repository checks:

```bash
python main.py -p Parafita123/DSSMV_ProjectReact_1231283_1231051 -pm npm --gradual-report false --check-source-code --debug
```

### 7. Run Dirty-Waters-based smells from NPM Smell Analyzer

Dirty-Waters-based smells must be executed explicitly.

Example:

```bash
npm-smell-analyzer --project "C:\Users\fpara\Desktop\DSSMV_ProjectReact_1231283_1231051-master" --repo Parafita123/DSSMV_ProjectReact_1231283_1231051 --dirty-waters-backend wsl --wsl-distro Ubuntu --dirty-waters-root /home/parafita/dirty-waters --smell deprecated-dependency
```

Another example:

```bash
npm-smell-analyzer --project "C:\Users\fpara\Desktop\DSSMV_ProjectReact_1231283_1231051-master" --repo Parafita123/DSSMV_ProjectReact_1231283_1231051 --dirty-waters-backend wsl --wsl-distro Ubuntu --dirty-waters-root /home/parafita/dirty-waters --smell no-source-code-link
```

To run all Dirty-Waters-based smells:

```bash
npm-smell-analyzer --project "C:\Users\fpara\Desktop\DSSMV_ProjectReact_1231283_1231051-master" --repo Parafita123/DSSMV_ProjectReact_1231283_1231051 --dirty-waters-backend wsl --wsl-distro Ubuntu --dirty-waters-root /home/parafita/dirty-waters --dirty-waters-all
```

### 8. Dirty-Waters report location

Dirty-Waters generates its own Markdown report inside the WSL environment.

A typical output path is:

```text
/home/<your-user>/dirty-waters/tool/results/results_<timestamp>/<commit>_static_summary.md
```

Example:

```text
/home/parafita/dirty-waters/tool/results/results_2026-05-17-16-22-19/09802c669fb76b9c5209bd9a6cf797b68c5c6657_static_summary.md
```

This Markdown report is the primary Dirty-Waters output and should be considered the source of truth for Dirty-Waters-based checks.

### 9. Dirty-Waters limitations

Dirty-Waters integration has the following limitations:

* it requires a GitHub repository and cannot analyze a purely local project without repository metadata;
* it is significantly slower than the local and Knip-based smells;
* in the tested setup, it was validated through WSL/Ubuntu;
* Dirty-Waters-based smells are executed separately and are not part of the default fast analysis flow.

Recommended workflow:

1. use NPM Smell Analyzer normally for local and Knip-based smells;
2. use Dirty-Waters-based smells only when repository-level supply chain analysis is needed.

---

## Configuration Files

The analyzer can optionally read execution settings from a JSON configuration file.

Two usage modes are supported:

* a configuration file placed in the root of the analyzed project;
* an explicit configuration file passed through `--config`.

The configuration file is optional. If no configuration file is found, the tool behaves normally and expects the required options through the command line.

Supported default filenames in the analyzed project root:

* `smellrc.json`
* `.smellrc.json`

### Example: local and Knip-based smells

Example configuration file:

```json
{
  "smells": ["all"],
  "unmaintained_threshold_months": 24
}
```

This configuration runs the default local and Knip-based smells.

### Example: Dirty-Waters-based smells

Example configuration file:

```json
{
  "smells": ["dirty-waters-all"],
  "repo": "owner/repository",
  "dirty_waters_backend": "wsl",
  "wsl_distro": "Ubuntu",
  "dirty_waters_root": "/home/your-user/dirty-waters"
}
```

This configuration runs all Dirty-Waters-based smells without requiring the same options to be repeated in every command.

### Command-line override

Command-line arguments take precedence over configuration values.

For example, if the configuration file contains:

```json
{
  "smells": ["all"]
}
```

the following command overrides that setting and runs only one smell:

```bash
npm-smell-analyzer --project "C:\path\to\project" --config "C:\path\to\config.json" --smell duplicate-versions
```

If `--config` points to a non-existing file, the tool fails explicitly with an error indicating that the configuration file could not be found.

---

## Testing and Validation

The prototype includes automated tests covering native detectors, integration scenarios, and external-tool adapter behavior.

Run the full test suite with:

```bash
python -m pytest
```

The validation strategy includes:

* unit tests for native detectors;
* integration tests over prepared npm projects;
* mock-based tests for Knip and Dirty-Waters adapters.

---

## Repository Structure

A simplified view of the repository structure is:

```text
src/
  analyzers/
  external_tools/
  smells/
  cli.py
  config.py
  models.py
  orchestrator.py
  report_writer.py

tests/
  unit/
  integration/
  mocks/

test_projects/
config_examples/
```

---

## Current Limitations

The current prototype has the following limitations:

* it focuses on npm projects;
* Dirty-Waters-based checks require external setup and GitHub metadata;
* some smells depend on installed `node_modules`;
* `unmaintained-package` is based on a heuristic threshold;
* the current reports are text/JSON-based;
* the tool reports indicators and warning signs, not confirmed vulnerabilities or attacks.

---

## License

This project is available under the license included in the repository.

