from src.smells.unmaintained_package import UnmaintainedPackageDetector


def test_unmaintained_package_detects_old_registry_metadata(monkeypatch):
    detector = UnmaintainedPackageDetector()

    manifest = {
        "dependencies": {
            "jest-fetch-mock": "^3.0.3"
        }
    }

    def fake_fetch(_package_name):
        return {
            "time": {
                "modified": "2022-06-19T04:11:37.355Z"
            }
        }

    monkeypatch.setattr(
        "src.smells.unmaintained_package._fetch_npm_package_metadata",
        fake_fetch,
    )

    findings = detector.detect(
        package_json=manifest,
        package_lock=None,
        project_path="dummy_project",
        unmaintained_threshold_months=24,
    )

    assert len(findings) == 1
    assert findings[0].smell == "unmaintained-package"
    assert findings[0].dependency == "jest-fetch-mock"


def test_unmaintained_package_ignores_recent_package(monkeypatch):
    detector = UnmaintainedPackageDetector()

    manifest = {
        "dependencies": {
            "react": "^18.2.0"
        }
    }

    def fake_fetch(_package_name):
        return {
            "time": {
                "modified": "2026-01-01T00:00:00.000Z"
            }
        }

    monkeypatch.setattr(
        "src.smells.unmaintained_package._fetch_npm_package_metadata",
        fake_fetch,
    )

    findings = detector.detect(
        package_json=manifest,
        package_lock=None,
        project_path="dummy_project",
        unmaintained_threshold_months=24,
    )

    assert findings == []