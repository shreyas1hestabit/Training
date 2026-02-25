import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

class SQLGenerator:
    def __init__(self, model="gemini-2.5-flash"):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in .env file")

        self.client=genai.Client(api_key=api_key)
        self.model = model

    def generate(self, question: str, schema: str) -> str:
        prompt = f"""
You are an expert SQL generator.

Database Schema:
{schema}

Rules:
- Return ONLY valid SQL.
- No explanations.
- No markdown.
- Do not use backticks.
- Use correct table and column names.

User Question:
{question}

SQL:
"""

        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
            config={
                "temperature":0,
                "max_output_tokens":300,
            })

        sql = response.text.strip()

        # Remove accidental markdown if any
        sql = sql.replace("```sql", "").replace("```", "").strip()

        return sql