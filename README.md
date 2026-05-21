# React Smell Analyzer

React Smell Analyzer is a command-line tool for detecting selected software supply chain smells in React/npm projects.

The current prototype combines:

- native local analysis of project files;
- dependency usage analysis through external tooling;
- selected repository-level checks through Dirty-Waters running via WSL.

The tool generates structured reports with findings and errors for each analysis run.

## Current Scope

The current prototype targets projects in the npm ecosystem and analyzes information derived from:

- `package.json`
- `package-lock.json`
- locally installed dependencies in `node_modules` (for selected smells)
- source code usage analysis through external tooling
- repository-level metadata through Dirty-Waters

The prototype is focused on lightweight, developer-oriented analysis and reporting.

It does **not**:

- execute dependency code during analysis;
- confirm malicious intent;
- prove exploitability;
- fully replace specialized ecosystem tools.

Instead, it highlights dependency-related smells and risk indicators that may deserve manual inspection.

## Currently Supported Smells

### Native local smells

These smells are detected directly by the tool through local parsing and rule-based analysis:

- `no-package-lock`
- `pinned-dependency`
- `url-dependency`
- `restrictive-constraint`
- `permissive-constraint`
- `duplicate-versions`
- `installation-scripts`
- `unmaintained-package`

### Knip-based smells

These smells are detected through integration with [Knip](https://knip.dev/):

- `unused-dependency`
- `missing-dependency`

### Dirty-Waters-based smells

These smells are detected through integration with [Dirty-Waters](https://github.com/chains-project/dirty-waters/) executed through **WSL/Ubuntu**:

- `deprecated-dependency`
- `no-source-code-link`
- `no-source-code-sha`
- `depends-on-fork`
- `no-build-attestation`
- `no-invalid-code-signature`
- `aliased-packages`

> **Note:** Dirty-Waters-based smells are external, slower, GitHub-dependent, and WSL/Ubuntu-oriented in the tested environment. They must be executed explicitly and are not part of the default `--all` run.

## Analysis Modes

The tool currently supports three main execution modes:

### 1. Default full analysis

Runs all default local and Knip-based smells:

```bash
react-smell-analyzer --project "C:\path\to\react-project" --all

### 2. Dirty-Waters full analysis

Runs all Dirty-Waters based smells:

```bash
react-smell-analyzer --project "C:\path\to\react-project" --repo owner/repo --dirty-waters-backend wsl --wsl-distro Ubuntu --dirty-waters-root /home/<your-user>/dirty-waters --dirty-waters-all

### 3. Specific smell analysis

Runs one or more explicitly selected smells:

```bash
react-smell-analyzer --project "C:\path\to\react-project" --smell duplicate-versions

Example with a Dirty-Waters smell:

```bash
react-smell-analyzer --project "C:\path\to\react-project" --repo owner/repo --dirty-waters-backend wsl --wsl-distro Ubuntu --dirty-waters-root /home/<your-user>/dirty-waters --smell deprecated-dependency


### Important Notes About Selected Smells

installation-scripts

This smell requires node_modules to be installed locally, because it inspects dependency package.json files inside the installed dependency tree.

unmaintained-package

This smell is heuristic-based. In the current prototype, it uses npm registry metadata and flags packages whose last registry modification is older than a defined threshold.

A flagged package is not necessarily abandoned, but it may deserve manual inspection.

## Requirements

### Core requirements

- Python 3.10 or higher
- npm-based project to analyze

### Additional requirements for Knip-based smells

For `unused-dependency` and `missing-dependency`, the target project must be able to run Knip.  
In practice, this usually means that the analyzed project should have Knip available locally or be able to execute it through `npx`.

For example, inside the target project:

```bash
npm install -D knip typescript @types/node


# Dirty-Waters Integration (WSL/Ubuntu)

The `react-smell-analyzer` supports a subset of smells through the external tool [Dirty-Waters](https://github.com/chains-project/dirty-waters/).

## Important Notes

Dirty-Waters-based smells are different from the local smells implemented directly in this project:

- they are slower to execute;
- they require a **GitHub repository** (`owner/repo`);
- they require a **GitHub API token**;
- in the tested environment, they were only validated successfully through **WSL/Ubuntu**.

Because of these requirements, Dirty-Waters-based smells are **not included in the default `--all` workflow** and should be executed explicitly.

> **Note:** Dirty-Waters-based smells are external, slower, GitHub-dependent, and WSL/Ubuntu-oriented in the tested environment. They must be executed explicitly and are not part of the default `--all` run.

---


## Requirements

To use Dirty-Waters-based smells, you need:

- Windows with **WSL** installed
- An **Ubuntu** distribution inside WSL
- A local clone of `dirty-waters` inside Ubuntu
- A valid **GitHub Personal Access Token**
- A project hosted on **GitHub**

---

## 1. Install WSL

Open **PowerShell as Administrator** and run:

```powershell
wsl --install -d Ubuntu

Restart the computer if requested.

After restarting, open Ubuntu and complete the initial setup by creating:

- a Linux username
- a Linux password

## 2. Prepara Ubuntu

Inside Ubuntu, install the required tools:

```ubuntu
sudo apt update
sudo apt install -y python3 python3-venv python3-pip git nodejs npm curl

## 3. Create a GitHub token

Create a fine-grained personal access token in GitHub with:

- Resource owner: your GitHub account
- Repository access: Only select repositories
- select the repository you want to analyze
- Repository permissions:
- Metadata -> Read-only
- Contents -> Read-only

This token is required by Dirty-Waters to access repository metadata.

## 4. Configure the GitHub token

### In Windows (required when running react-smell-analyzer from CMD/PowerShell)

In the same terminal where you run the analyzer:

```bash
set GITHUB_API_TOKEN=YOUR_TOKEN_HERE

To make it persistent for future terminals:

```bash
setx GITHUB_API_TOKEN "YOUR_TOKEN_HERE"

### In Ubuntu/WSL (recommended for standalone Dirty-Waters usage)

```ubuntu
export GITHUB_API_TOKEN='YOUR_TOKEN_HERE'

To make it persistent:

```ubuntu
echo 'export GITHUB_API_TOKEN="YOUR_TOKEN_HERE"' >> ~/.bashrc
source ~/.bashrc

## 5. Clone and install Dirty-Waters inside Ubuntu

Inside Ubuntu:

```ubuntu
cd ~
git clone https://github.com/chains-project/dirty-waters.git
cd dirty-waters
python3 -m venv venv
source venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .

At this point, Dirty-Waters should be available inside WSL.

## 6. Standalone Dirty-Waters execution

To validate that Dirty-Waters works correctly in Ubuntu:

```ubuntu
cd ~/dirty-waters/tool
python main.py -p OWNER/REPOSITORY -pm npm --gradual-report false --check-deprecated --debug

Example:

```ubuntu
cd ~/dirty-waters/tool
python main.py -p Parafita123/DSSMV_ProjectReact_1231283_1231051 -pm npm --gradual-report false --check-deprecated --debug

Another example for source-code repository checks:

```ubuntu
python main.py -p Parafita123/DSSMV_ProjectReact_1231283_1231051 -pm npm --gradual-report false --check-source-code --debug

## 7. Running Dirty-Waters-based smells from react-smell-analyzer

Dirty-Waters-based smells must be executed explicitly.

Example:

```bash
react-smell-analyzer --project "C:\Users\fpara\Desktop\DSSMV_ProjectReact_1231283_1231051-master" --repo Parafita123/DSSMV_ProjectReact_1231283_1231051 --dirty-waters-backend wsl --wsl-distro Ubuntu --dirty-waters-root /home/parafita/dirty-waters --smell deprecated-dependency

Another example:

```bash
react-smell-analyzer --project "C:\Users\fpara\Desktop\DSSMV_ProjectReact_1231283_1231051-master" --repo Parafita123/DSSMV_ProjectReact_1231283_1231051 --dirty-waters-backend wsl --wsl-distro Ubuntu --dirty-waters-root /home/parafita/dirty-waters --smell no-source-code-link

## 8. Report location

Dirty-Waters generates its own Markdown report inside the WSL environment.

A typical output path is:

/home/<your-user>/dirty-waters/tool/results/results_<timestamp>/<commit>_static_summary.md

Example:

/home/parafita/dirty-waters/tool/results/results_2026-05-17-16-22-19/09802c669fb76b9c5209bd9a6cf797b68c5c6657_static_summary.md

This Markdown report is the primary output of Dirty-Waters and should be considered the source of truth for Dirty-Waters-based checks.

## 9. Current limitations

Dirty-Waters integration has the following limitations:

- it requires a GitHub repository and cannot analyze a purely local project without repository metadata;
- it is significantly slower than the local smells and Knip-based smells;
- in the tested setup, it was only validated successfully through WSL/Ubuntu;
- Dirty-Waters-based smells are therefore executed separately and are not part of the default fast analysis flow.

For this reason, the recommended workflow is:

use react-smell-analyzer normally for local/fast smells;
use Dirty-Waters-based smells only when repository-level supply-chain analysis is needed.



## Configuration Files

The analyzer can optionally read its execution settings from a JSON configuration file.

Two usage modes are supported:

- a configuration file placed in the root of the analyzed project;
- an explicit configuration file passed through `--config`.

The configuration file is optional. If no configuration file is found, the tool behaves normally and expects the required options through the command line.

Supported default filenames in the analyzed project root:

- `smellrc.json`
- `.smellrc.json`

### Example: local and Knip smells

Example configuration file:

```json
{
  "smells": ["all"],
  "unmaintained_threshold_months": 24
}

This configuration runs the default local and Knip-based smells.


## Dirty-Waters config example

Example configuration file:

```json
{
  "smells": ["dirty-waters-all"],
  "repo": "owner/repository",
  "dirty_waters_backend": "wsl",
  "wsl_distro": "Ubuntu",
  "dirty_waters_root": "/home/your-user/dirty-waters"
}

This configuration runs all Dirty-Waters-based smells without requiring the same options to be repeated in every command.


### Command-line override

Command-line arguments take precedence over configuration values.

For example, if the configuration file contains:

```json
{
  "smells": ["all"]
}

the following command will override that setting and run only one smell:

```bash
react-smell-analyzer --project "C:\path\to\project" --config "C:\path\to\config.json" --smell duplicate-versions

Note:
If `--config` points to a non-existing file, the tool will fail explicitly with an error indicating that the configuration file could not be found.

