import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=api_key)


print("=== AI Job Description Assistant ===")
print()
print("Choose an option:")
print("1. Extract skills")
print("2. Summarize job")
print("3. Generate interview questions")

choice = input("\nEnter your choice (1-3): ")


print("\nPaste the job description below.")
print("Press Enter twice when you're finished.\n")

lines = []

while True:
    line = input()

    if line == "":
        break

    lines.append(line)

job_description = "\n".join(lines)


if choice == "1":

    prompt = f"""
Analyze the following job description and extract the important requirements.

Return the result in exactly this format:

Required Skills:
- skill 1
- skill 2

Nice to Have:
- skill 1
- skill 2

Experience:
- experience requirement

Job Description:
{job_description}
"""


elif choice == "2":

    prompt = f"""
Summarize the following job description for a job candidate.

Return the result in exactly this format:

Role:
- ...

Main Responsibilities:
- ...
- ...
- ...

Required Skills:
- ...
- ...

Experience:
- ...

Job Description:
{job_description}
"""


elif choice == "3":

    prompt = f"""
Analyze the following job description and generate interview questions
that a candidate should prepare for.

Return the result in exactly this format:

Technical Questions:
1. ...
2. ...
3. ...

Behavioral Questions:
1. ...
2. ...
3. ...

Job-Specific Questions:
1. ...
2. ...

Job Description:
{job_description}
"""


else:

    print("\nInvalid choice. Please choose 1, 2, or 3.")
    exit()


response = client.models.generate_content(
    model="gemini-3.6-flash",
    contents=prompt
)

print("\n=== Result ===\n")
print(response.text)
