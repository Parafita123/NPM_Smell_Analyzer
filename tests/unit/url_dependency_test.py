from src.smells.url_dependency import UrlDependencyDetector


def test_url_dependency_detects_git_url():
    detector = UrlDependencyDetector()

    manifest = {
        "dependencies": {
            "mylib": "git+https://github.com/example/repo.git",
            "react": "^18.2.0",
        }
    }

    findings = detector.detect(
        package_json=manifest,
        package_lock=None,
        project_path="dummy_project",
    )

    assert len(findings) == 1
    assert findings[0].smell == "url-dependency"
    assert findings[0].dependency == "mylib"


def test_url_dependency_detects_http_url():
    detector = UrlDependencyDetector()

    manifest = {
        "dependencies": {
            "custom-lib": "https://example.com/custom-lib.tgz",
            "react": "^18.2.0",
        }
    }

    findings = detector.detect(
        package_json=manifest,
        package_lock=None,
        project_path="dummy_project",
    )

    assert len(findings) == 1
    assert findings[0].dependency == "custom-lib"


def test_url_dependency_ignores_registry_versions():
    detector = UrlDependencyDetector()

    manifest = {
        "dependencies": {
            "react": "^18.2.0",
            "lodash": "~4.17.21",
            "axios": "1.7.2",
        }
    }

    findings = detector.detect(
        package_json=manifest,
        package_lock=None,
        project_path="dummy_project",
    )

    assert findings == []


def test_url_dependency_detects_multiple_url_dependencies():
    detector = UrlDependencyDetector()

    manifest = {
        "dependencies": {
            "lib-a": "git+https://github.com/example/a.git",
            "lib-b": "https://example.com/lib-b.tgz",
            "react": "^18.2.0",
        }
    }

    findings = detector.detect(
        package_json=manifest,
        package_lock=None,
        project_path="dummy_project",
    )

    detected_dependencies = {finding.dependency for finding in findings}

    assert len(findings) == 2
    assert "lib-a" in detected_dependencies
    assert "lib-b" in detected_dependencies