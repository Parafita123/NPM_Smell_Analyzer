from src.smells.no_package_lock import NoPackageLockDetector
from src.smells.pinned_dependency import PinnedDependencyDetector
from src.smells.url_dependency import UrlDependencyDetector
from src.smells.restrictive_constraint import RestrictiveConstraintDetector
from src.smells.permissive_constraint import PermissiveConstraintDetector
from src.smells.duplicate_versions import DuplicateVersionsDetector

SMELL_REGISTRY = {
    "no-package-lock": NoPackageLockDetector(),
    "pinned-dependency": PinnedDependencyDetector(),
    "url-dependency": UrlDependencyDetector(),
    "restrictive-constraint": RestrictiveConstraintDetector(),
    "permissive-constraint": PermissiveConstraintDetector(),
    "duplicate-versions": DuplicateVersionsDetector(),
}