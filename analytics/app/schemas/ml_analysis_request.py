from pydantic import BaseModel

class MLAnalysisRequest(BaseModel):
    targetColumn: str