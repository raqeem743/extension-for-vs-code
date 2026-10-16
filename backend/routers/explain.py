
from fastapi import APIRouter, HTTPException
from google.genai import errors

from models.schema import ErrorRequest, ErrorResponse
from services.llm import explain_with_gemini


router = APIRouter()


@router.post("/explain-error", response_model=ErrorResponse)
def explain_error(request: ErrorRequest):
    try:
        return explain_with_gemini(request)

    except errors.APIError as exc:
        status = getattr(exc, "code", None)

        print(f"Gemini API error: {type(exc).__name__}: {exc}")

        if status == 503:
            raise HTTPException(
                status_code=503,
                detail=(
                    "Gemini is temporarily unavailable. "
                    "Please try again later."
                ),
            ) from exc

        if status == 429:
            raise HTTPException(
                status_code=429,
                detail=(
                    "Gemini quota or rate limit reached. "
                    "Check your API usage and limits."
                ),
            ) from exc

        raise HTTPException(
            status_code=502,
            detail="Gemini request failed. Check the backend terminal.",
        ) from exc

    except RuntimeError as exc:
        print(f"Configuration or response error: {exc}")
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        print(f"Unexpected error: {type(exc).__name__}: {exc}")
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred in the backend.",
        ) from exc
