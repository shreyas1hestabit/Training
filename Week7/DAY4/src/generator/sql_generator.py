# # # import os
# # # from dotenv import load_dotenv
# # # from google import genai

# # # load_dotenv()

# # # class SQLGenerator:
# # #     def __init__(self, model="gemini-2.5-flash"):
# # #         api_key = os.getenv("GEMINI_API_KEY")
# # #         if not api_key:
# # #             raise ValueError("GEMINI_API_KEY not found in .env file")

# # #         self.client=genai.Client(api_key=api_key)
# # #         self.model = model

# # #     def generate(self, question: str, schema: str) -> str:
# # #         if not question:
# # #             return "Error: No questions provided"
# # #         prompt = f"""
# # # You are an expert SQL generator.

# # # Database Schema:
# # # {schema}

# # # Rules:
# # # - Return ONLY valid SQL.
# # # - No explanations.
# # # - No markdown.
# # # - Do not use backticks.
# # # - Use correct table and column names.

# # # User Question:
# # # {question}

# # # SQL:
# # # """
        
# # #         # response = self.client.models.generate_content(
# # #         #     model=self.model,
# # #         #     contents=prompt,
# # #         #     config={
# # #         #         "temperature":0,
# # #         #         "max_output_tokens":300,
# # #         #     })

# # #         # sql = response.text.strip()

# # #         # # Remove accidental markdown if any
# # #         # sql = sql.replace("```sql", "").replace("```", "").strip()

# # #         # return sql
# # #         try:
# # #             response = self.client.models.generate_content(
# # #                 model=self.model,
# # #                 contents=prompt
# # #             )
# # #             if response and hasattr(response, 'text') and response.text:
# # #                 sql = response.text.strip()
# # #                 return sql.replace("```sql", "").replace("```", "").strip()
# # #             return "Error: Model returned empty response."
# # #         except Exception as e:
# # #             return f"Error during generation: {str(e)}"

# # import os
# # from dotenv import load_dotenv
# # from google import genai

# # load_dotenv()

# # class SQLGenerator:
# #     def __init__(self, model="gemini-2.0-flash-lite"):
# #         api_key = os.getenv("GEMINI_API_KEY")
# #         if not api_key:
# #             raise ValueError("GEMINI_API_KEY not found in .env file")

# #         self.client = genai.Client(api_key=api_key)
# #         self.model = model

# #     def _build_prompt(self, question: str, context: str, mode: str = "rag") -> str:
# #         if mode == "sql":
# #             return f"""
# # You are an expert SQL generator.

# # Database Schema:
# # {context}

# # Rules:
# # - Return ONLY valid SQL.
# # - No explanations.
# # - No markdown.
# # - Do not use backticks.
# # - Use correct table and column names.

# # User Question:
# # {question}

# # SQL:
# # """
# #         else:  # rag or image mode
# #             return f"""
# # You are a helpful assistant. Answer the user's question using only the provided context.

# # Context:
# # {context}

# # Question:
# # {question}

# # Answer:
# # """

# #     def generate(self, question: str, context: str, mode: str = "rag") -> str:
# #         if not question or not question.strip():
# #             return "Error: No question provided."

# #         prompt = self._build_prompt(question, context, mode)

# #         try:
# #             response = self.client.models.generate_content(
# #                 model=self.model,
# #                 contents=prompt
# #             )
# #             if response and hasattr(response, 'text') and response.text:
# #                 result = response.text.strip()
# #                 if mode == "sql":
# #                     result = result.replace("```sql", "").replace("```", "").strip()
# #                 return result
# #             return "Error: Model returned empty response."
# #         except Exception as e:
# #             return f"Error during generation: {str(e)}"

# # import os
# # from dotenv import load_dotenv
# # from google import genai

# # load_dotenv()

# # class SQLGenerator:
# #     def __init__(self, model="gemini-2.5-flash"):
# #         api_key = os.getenv("GEMINI_API_KEY")
# #         if not api_key:
# #             raise ValueError("GEMINI_API_KEY not found in .env file")

# #         self.client=genai.Client(api_key=api_key)
# #         self.model = model

# #     def generate(self, question: str, schema: str) -> str:
# #         if not question:
# #             return "Error: No questions provided"
# #         prompt = f"""
# # You are an expert SQL generator.

# # Database Schema:
# # {schema}

# # Rules:
# # - Return ONLY valid SQL.
# # - No explanations.
# # - No markdown.
# # - Do not use backticks.
# # - Use correct table and column names.

# # User Question:
# # {question}

# # SQL:
# # """
        
# #         # response = self.client.models.generate_content(
# #         #     model=self.model,
# #         #     contents=prompt,
# #         #     config={
# #         #         "temperature":0,
# #         #         "max_output_tokens":300,
# #         #     })

# #         # sql = response.text.strip()

# #         # # Remove accidental markdown if any
# #         # sql = sql.replace("```sql", "").replace("```", "").strip()

# #         # return sql
# #         try:
# #             response = self.client.models.generate_content(
# #                 model=self.model,
# #                 contents=prompt
# #             )
# #             if response and hasattr(response, 'text') and response.text:
# #                 sql = response.text.strip()
# #                 return sql.replace("```sql", "").replace("```", "").strip()
# #             return "Error: Model returned empty response."
# #         except Exception as e:
# #             return f"Error during generation: {str(e)}"

# import os
# from dotenv import load_dotenv
# # from google import genai
# from openai import OpenAI

# load_dotenv()

# class SQLGenerator:
#     def __init__(self, model="llama-3.1-8b-instant"):
#         api_key = os.getenv("GROQ_API_KEY")
#         if not api_key:
#             raise ValueError("GROQ_API_KEY not found in .env file")

#         self.client = OpenAI.Client(api_key=api_key)
#         self.model = model

#     def _build_prompt(self, question: str, context: str, mode: str = "rag") -> str:
#         if mode == "sql":
#             return f"""
# You are an expert SQL generator.

# Database Schema:
# {context}

# Rules:
# - Return ONLY valid SQL.
# - No explanations.
# - No markdown.
# - Do not use backticks.
# - Use correct table and column names.

# User Question:
# {question}

# SQL:
# """
#         else:  # rag or image mode
#             return f"""
# You are a helpful assistant. Answer the user's question using only the provided context.

# Context:
# {context}

# Question:
# {question}

# Answer:
# """

#     def generate(self, question: str, context: str, mode: str = "rag") -> str:
#         if not question or not question.strip():
#             return "Error: No question provided."

#         prompt = self._build_prompt(question, context, mode)
#         cache_key = f"{mode}::{question.strip()}"
#         if hasattr(self, '_cache') and cache_key in self._cache:
#             print("[CACHE HIT]")
#             return self._cache[cache_key]
#         if not hasattr(self, '_cache'):
#             self._cache = {}

#         prompt = self._build_prompt(question, context, mode)
#         try:
#             response = self.client.models.generate_content(
#                 model=self.model,
#                 contents=prompt
#             )
#             if response and hasattr(response, 'text') and response.text:
#                 result = response.text.strip()
#                 if mode == "sql":
#                     result = result.replace("```sql", "").replace("```", "").strip()
#                     self._cache[cache_key]=result
#                 return result
#             return "Error: Model returned empty response."
#         except Exception as e:
#             return f"Error during generation: {str(e)}"

import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

class SQLGenerator:
    def __init__(self, model="llama-3.1-8b-instant"):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY not found in .env file")

        self.client = Groq(api_key=api_key)
        self.model = model
        self._cache = {}

    def _build_prompt(self, question: str, context: str, mode: str = "rag") -> str:
        if mode == "sql":
            return f"""
You are an expert SQL generator.

Database Schema:
{context}

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
        else:
            return f"""
You are a helpful assistant. Answer the user's question using only the provided context.

Context:
{context}

Question:
{question}

Answer:
"""

    def generate(self, question: str, context: str, mode: str = "rag") -> str:
        if not question or not question.strip():
            return "Error: No question provided."

        # Cache check
        cache_key = f"{mode}::{question.strip()}"
        if cache_key in self._cache:
            print("[CACHE HIT]")
            return self._cache[cache_key]

        prompt = self._build_prompt(question, context, mode)

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0
            )

            result = response.choices[0].message.content.strip()

            if not result:
                return "Error: Model returned empty response."

            if mode == "sql":
                result = result.replace("```sql", "").replace("```", "").strip()

            self._cache[cache_key] = result
            return result

        except Exception as e:
            return f"Error during generation: {str(e)}"