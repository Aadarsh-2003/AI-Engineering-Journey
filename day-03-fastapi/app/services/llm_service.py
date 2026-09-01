import os

from dotenv import load_dotenv
from google import genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=api_key)


def analyze_job_description(job_description: str):

    prompt = f"""
Analyze the following job description.

Extract:
1. Required technical skills
2. Nice-to-have skills
3. Expected experience level

Return the result in exactly this format:

Required Skills:
- skill 1
- skill 2

Nice to Have:
- skill 1
- skill 2

Experience Level:
- Junior/Mid-level/Senior

Job Description:
{job_description}
"""

    try:
        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt
        )

        return {
            "analysis": response.text
        }

    except Exception as e:
        return {
            "error": "Failed to analyze job description",
            "details": str(e)
        }