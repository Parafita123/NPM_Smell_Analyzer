from src.smells.pinned_dependency import PinnedDependencyDetector


def test_pinned_dependency_detects_exact_version():
    detector = PinnedDependencyDetector()

    manifest = {
        "dependencies": {
            "react": "18.2.0",
            "lodash": "^4.17.21",
        }
    }

    findings = detector.detect(
        package_json=manifest,
        package_lock=None,
        project_path="dummy_project",
    )

    assert len(findings) == 1
    assert findings[0].smell == "pinned-dependency"
    assert findings[0].dependency == "react"


def test_pinned_dependency_ignores_range_versions():
    detector = PinnedDependencyDetector()

    manifest = {
        "dependencies": {
            "react": "^18.2.0",
            "lodash": "~4.17.21",
            "axios": ">=1.0.0",
        }
    }

    findings = detector.detect(
        package_json=manifest,
        package_lock=None,
        project_path="dummy_project",
    )

    assert findings == []


def test_pinned_dependency_detects_multiple_exact_versions():
    detector = PinnedDependencyDetector()

    manifest = {
        "dependencies": {
            "react": "18.2.0",
            "axios": "1.7.2",
            "lodash": "^4.17.21",
        }
    }

    findings = detector.detect(
        package_json=manifest,
        package_lock=None,
        project_path="dummy_project",
    )

    detected_dependencies = {finding.dependency for finding in findings}

    assert len(findings) == 2
    assert "react" in detected_dependencies
    assert "axios" in detected_dependencies