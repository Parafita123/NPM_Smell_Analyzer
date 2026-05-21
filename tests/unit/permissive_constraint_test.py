from src.smells.permissive_constraint import PermissiveConstraintDetector


def test_permissive_constraint_detects_wildcard():
    detector = PermissiveConstraintDetector()

    manifest = {
        "dependencies": {
            "open-lib": "*",
            "react": "^18.2.0",
        }
    }

    findings = detector.detect(
        package_json=manifest,
        package_lock=None,
        project_path="dummy_project",
    )

    assert len(findings) == 1
    assert findings[0].smell == "permissive-constraint"
    assert findings[0].dependency == "open-lib"


def test_permissive_constraint_detects_open_ended_range():
    detector = PermissiveConstraintDetector()

    manifest = {
        "dependencies": {
            "open-lib": ">=1.0.0",
            "react": "^18.2.0",
        }
    }

    findings = detector.detect(
        package_json=manifest,
        package_lock=None,
        project_path="dummy_project",
    )

    assert len(findings) == 1
    assert findings[0].dependency == "open-lib"


def test_permissive_constraint_ignores_normal_versions():
    detector = PermissiveConstraintDetector()

    manifest = {
        "dependencies": {
            "react": "^18.2.0",
            "axios": "~1.7.2",
        }
    }

    findings = detector.detect(
        package_json=manifest,
        package_lock=None,
        project_path="dummy_project",
    )

    assert findings == []