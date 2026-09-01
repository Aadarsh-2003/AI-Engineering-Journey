from pydantic import BaseModel, Field

class JobRequest(BaseModel):
    job_description: str = Field(min_length=1)