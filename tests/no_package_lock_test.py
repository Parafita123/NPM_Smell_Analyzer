from src.smells.no_package_lock import NoPackageLockDetector


def test_no_package_lock_detects_missing_lockfile(tmp_path):
    detector = NoPackageLockDetector()

    findings = detector.detect(
        package_json={"dependencies": {"react": "^18.2.0"}},
        package_lock=None,
        project_path=str(tmp_path),
    )

    assert len(findings) == 1
    assert findings[0].smell == "no-package-lock"
    assert findings[0].dependency is None


def test_no_package_lock_ignores_existing_lockfile(tmp_path):
    detector = NoPackageLockDetector()

    lockfile_path = tmp_path / "package-lock.json"
    lockfile_path.write_text('{"lockfileVersion": 3}', encoding="utf-8")

    findings = detector.detect(
        package_json={"dependencies": {"react": "^18.2.0"}},
        package_lock={"lockfileVersion": 3},
        project_path=str(tmp_path),
    )

    assert findings == []