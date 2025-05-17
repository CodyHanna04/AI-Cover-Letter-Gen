import os
from dotenv import load_dotenv
import openai

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# 1) Collect inputs
job_desc = input("Paste the job description URL or text:\n")
resume_bullets = input("Paste your resume bullet points (comma-separated):\n")

# 2) Build the prompt
prompt = f"""
Write a concise, professional cover letter. 
Job description: {job_desc}
My resume highlights: {resume_bullets}

Please format with:
[Your Name]
[Your Address]
[Date]

[Greeting],

[Body – 3 concise paragraphs]

[Sincerely,]
[Your Name]
"""

# 3) Call OpenAI
response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[{"role":"user","content": prompt}],
    temperature=0.7,
    max_tokens=500,
)

# 4) Output
print("\n--- Generated Cover Letter ---\n")
print(response.choices[0].message.content.strip())
