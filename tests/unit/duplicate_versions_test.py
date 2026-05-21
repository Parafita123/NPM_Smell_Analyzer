from src.smells.duplicate_versions import DuplicateVersionsDetector


def test_duplicate_versions_detects_same_package_with_multiple_versions():
    detector = DuplicateVersionsDetector()

    lockfile = {
        "name": "sample-project",
        "lockfileVersion": 3,
        "packages": {
            "": {
                "name": "sample-project",
                "dependencies": {
                    "lodash": "^4.17.21"
                },
            },
            "node_modules/lodash": {
                "version": "4.17.21"
            },
            "node_modules/some-lib/node_modules/lodash": {
                "version": "4.17.20"
            },
        },
    }

    findings = detector.detect(
        package_json=None,
        package_lock=lockfile,
        project_path="dummy_project",
    )

    assert len(findings) == 1
    assert findings[0].smell == "duplicate-versions"
    assert findings[0].dependency == "lodash"


def test_duplicate_versions_ignores_single_resolved_version():
    detector = DuplicateVersionsDetector()

    lockfile = {
        "name": "sample-project",
        "lockfileVersion": 3,
        "packages": {
            "": {
                "name": "sample-project",
                "dependencies": {
                    "lodash": "^4.17.21"
                },
            },
            "node_modules/lodash": {
                "version": "4.17.21"
            },
        },
    }

    findings = detector.detect(
        package_json=None,
        package_lock=lockfile,
        project_path="dummy_project",
    )

    assert findings == []