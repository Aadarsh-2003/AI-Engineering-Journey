from pydantic import BaseModel, Field

class JobRequest(BaseModel):
    job_description: str = Field(min_length=1)

class JobAnalysis(BaseModel):
    required_skills: list[str]
    nice_to_have: list[str]
    experience_level: str

class QuestionsRequest(BaseModel):
    job_description: str = Field(min_length=1)
    number_of_questions: int = Field(default=5, ge=1, le=10)


class QuestionsResponse(BaseModel):
    questions: list[str]