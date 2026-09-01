from fastapi import FastAPI
from models import JobRequest
from services.llm_service import analyze_job_description

app = FastAPI()


@app.post("/analyze")
def analyze_job(request: JobRequest):
    result = analyze_job_description(request.job_description)
    return result
    

@app.get("/")
def read_root():
    return {"message": "AI Job Analyzer API"}

@app.get("/health")
def read_health():
    return {
            "status": "healthy",
            "service": "AI Job Analyzer"
        }