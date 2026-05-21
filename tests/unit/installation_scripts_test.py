import json

from src.smells.installation_scripts import InstallationScriptsDetector


def test_installation_scripts_detects_postinstall(tmp_path):
    detector = InstallationScriptsDetector()

    project_dir = tmp_path / "sample_project"
    package_dir = project_dir / "node_modules" / "esbuild"
    package_dir.mkdir(parents=True)

    package_json_path = package_dir / "package.json"
    package_json_path.write_text(
        json.dumps(
            {
                "name": "esbuild",
                "version": "0.25.0",
                "scripts": {
                    "postinstall": "node install.js"
                },
            }
        ),
        encoding="utf-8",
    )

    findings = detector.detect(
        package_json=None,
        package_lock=None,
        project_path=str(project_dir),
    )

    assert len(findings) == 1
    assert findings[0].smell == "installation-scripts"
    assert findings[0].dependency == "esbuild"


def test_installation_scripts_ignores_dependencies_without_install_scripts(tmp_path):
    detector = InstallationScriptsDetector()

    project_dir = tmp_path / "sample_project"
    package_dir = project_dir / "node_modules" / "left-pad"
    package_dir.mkdir(parents=True)

    package_json_path = package_dir / "package.json"
    package_json_path.write_text(
        json.dumps(
            {
                "name": "left-pad",
                "version": "1.3.0",
                "scripts": {
                    "test": "echo ok"
                },
            }
        ),
        encoding="utf-8",
    )

    findings = detector.detect(
        package_json=None,
        package_lock=None,
        project_path=str(project_dir),
    )

    assert findings == []