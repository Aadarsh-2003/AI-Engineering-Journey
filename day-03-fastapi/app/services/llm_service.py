import os
import logging

from dotenv import load_dotenv
from google import genai
from models import JobAnalysis, QuestionsResponse

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=api_key)


def analyze_job_description(job_description: str):

    prompt = f"""
        You are an AI job skills analyzer.

        Analyze the following job description.

        Extract:
        1. Required technical skills
        2. Nice-to-have technical skills
        3. Expected experience level

        Use only information supported by the job description.
        Do not invent, assume, or add skills or experience requirements
        that are not present in the provided text.

        Job Description:
        {job_description}
        """

    try:

        logger.info("Calling Gemini for job analysis")

        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt,
            config={
                "response_mime_type": "application/json",
                "response_schema": JobAnalysis,
            },
        )

        logger.info("Gemini response received for job analysis")

        return JobAnalysis.model_validate_json(response.text)   

    except Exception as e:
        logger.exception("Gemini request failed during job analysis")
        raise RuntimeError("Failed to analyze job description") from e
    
def generate_interview_questions(
    job_description: str,
    number_of_questions: int
):

    prompt = f"""
You are an AI technical interview question generator.

Analyze the following job description and generate
{number_of_questions} technical interview questions
that are relevant to the skills and requirements mentioned.

Use only information supported by the job description.
Do not generate questions about technologies that are
not mentioned or reasonably supported by the job description.

Job Description:
{job_description}
"""

    try:

        logger.info("Calling Gemini for interview questions")

        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt,
            config={
                "response_mime_type": "application/json",
                "response_schema": QuestionsResponse,
            },
        )

        logger.info("Gemini response received for interview questions")
        return QuestionsResponse.model_validate_json(response.text)

    except Exception as e:
        logger.exception("Gemini request failed while generating interview questions")
        raise RuntimeError("Failed to analyze job description") from e