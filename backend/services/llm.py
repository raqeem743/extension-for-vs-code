
import os

from dotenv import load_dotenv
from google import genai
from google.genai import types

from models.schema import ErrorRequest, ErrorResponse


# .env is located directly inside the backend folder.
BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BACKEND_DIR, ".env"))


def explain_with_gemini(request: ErrorRequest) -> ErrorResponse:
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is missing from backend/.env"
        )

    prompt = f"""
You are a programming tutor. Explain this error in simple,
beginner-friendly English.

Return:
- explanation: what the error means
- cause: the likely reason
- fix: practical steps or corrected code

Do not invent information. If uncertain, say what needs checking.

Language: {request.language}
File: {request.file_name}

Error:
{request.error}

Relevant code:
{request.code}
"""

    with genai.Client(api_key=api_key) as client:
        response = client.models.generate_content(
            model="gemini-3.8-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=ErrorResponse,
            ),
        )

    if not response.text:
        raise RuntimeError("Gemini returned an empty response.")

    return ErrorResponse.model_validate_json(response.text)
