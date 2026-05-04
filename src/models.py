from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any


@dataclass
class Finding:
    smell: str
    dependency: str | None
    severity: str
    evidence: Dict[str, Any]
    message: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class AnalysisResult:
    project_path: str
    selected_smells: List[str]
    findings: List[Finding] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "project_path": self.project_path,
            "selected_smells": self.selected_smells,
            "findings": [f.to_dict() for f in self.findings],
            "errors": self.errors,
            "total_findings": len(self.findings),
        }