from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path


@dataclass
class GeneratorConfig:
    n_aircraft: int = 100
    n_airports: int = 40
    n_days: int = 90
    start_date: datetime = field(default_factory=lambda: datetime(2024, 7, 1))
    seed: int = 42
    output_dir: Path = field(default_factory=Path)

    @property
    def n_hours(self) -> int:
        return self.n_days * 24
