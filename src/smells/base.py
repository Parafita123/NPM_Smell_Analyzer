from abc import ABC, abstractmethod
from typing import Any
from src.models import Finding


class SmellDetector(ABC):
    smell_name: str

    @abstractmethod
    def detect(self, **kwargs: Any) -> list[Finding]:
        pass