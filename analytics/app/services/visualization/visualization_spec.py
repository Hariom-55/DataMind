from dataclasses import dataclass, field
from typing import Any

from app.services.visualization.visualization_types import VisualizationType
from app.services.visualization.visualization_limits import MAX_VISUALIZATION_POINTS, evenly_spaced_sample

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
        sampled_data = evenly_spaced_sample(self.data)
        metadata = dict(self.metadata)
        if len(self.data) > MAX_VISUALIZATION_POINTS:
            metadata["payloadLimit"] = {
                "maxPoints": MAX_VISUALIZATION_POINTS,
                "totalPoints": len(self.data),
                "returnedPoints": len(sampled_data),
                "sampling": "evenly_spaced",
            }
        return {
            "type":self.type.value,
            "title":self.title,
            "description": self.description,
            "x": self.x,
            "y":self.y,
            "data": sampled_data,
            "metadata": metadata,
        }
