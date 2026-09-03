from fastapi import FastAPI, HTTPException
from models import JobRequest, QuestionsRequest
from services.llm_service import analyze_job_description, generate_interview_questions

app = FastAPI()
    

@app.get("/")
def read_root():
    return {"message": "AI Job Analyzer API"}

@app.get("/health")
def read_health():
    return {
            "status": "healthy",
            "service": "AI Job Analyzer"
        }

@app.post("/analyze")
def analyze_job(request: JobRequest):

    try:
        result = analyze_job_description(request.job_description)
        return result

    except RuntimeError:
        raise HTTPException(
            status_code=500,
            detail="Failed to analyze job description"
        )

@app.post("/questions")
def generate_questions(request: QuestionsRequest):

    try:
        result = generate_interview_questions(
            request.job_description,
            request.number_of_questions
        )

        return result

    except RuntimeError:
        raise HTTPException(
            status_code=500,
            detail="Failed to generate interview questions"
        )