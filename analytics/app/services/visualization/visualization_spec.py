from dataclasses import dataclass, field
from typing import Any

from app.services.visualization.visualization_types import VisualizationType

@dataclass(frozen=True)
class VisualizationSpec:
    type: VisualizationType
    title: str
    data: list[dict[str, Any]]
    x: str |None=None
    y: str| None =None
    description: str | None = None
    metadata : dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str,Any]:
        return {
            "type":self.type.value,
            "title":self.title,
            "description": self.description,
            "x": self.x,
            "y":self.y,
            "data": self.data,
            "metadata": self.metadata,
        }