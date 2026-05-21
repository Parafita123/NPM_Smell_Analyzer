from src.smells.restrictive_constraint import RestrictiveConstraintDetector


def test_restrictive_constraint_detects_tilde_version():
    detector = RestrictiveConstraintDetector()

    manifest = {
        "dependencies": {
            "legacy-lib": "~2.3.1",
            "react": "^18.2.0",
        }
    }

    findings = detector.detect(
        package_json=manifest,
        package_lock=None,
        project_path="dummy_project",
    )

    assert len(findings) == 1
    assert findings[0].smell == "restrictive-constraint"
    assert findings[0].dependency == "legacy-lib"


def test_restrictive_constraint_ignores_non_restrictive_versions():
    detector = RestrictiveConstraintDetector()

    manifest = {
        "dependencies": {
            "react": "^18.2.0",
            "axios": ">=1.0.0",
            "lodash": "*",
        }
    }

    findings = detector.detect(
        package_json=manifest,
        package_lock=None,
        project_path="dummy_project",
    )

    assert findings == []