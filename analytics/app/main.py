from fastapi import FastAPI

from app.api.analysis import router as analysis_router

app = FastAPI(
    title = "DataMind Analysis Engine",
    version = "1.0.0"
)

@app.get("/health")
def health_check():
    return {
        "status" : "UP",
        "service" : "datamind-analysis"
    }

app.include_router(analysis_router)