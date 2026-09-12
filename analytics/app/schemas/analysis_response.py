from typing import Any, Optional

from pydantic import BaseModel

class AnalysisResponse(BaseModel):
    status: str
    result: Optional[dict[str, Any]] = None
    error: Optional[str] = None
    