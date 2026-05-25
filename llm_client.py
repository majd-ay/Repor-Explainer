import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

DEFAULT_MODEL = "gemini-2.5-flash-lite"


def get_model_name() -> str:
    return os.getenv("GEMINI_MODEL", DEFAULT_MODEL)


def _is_quota_error(error: Exception) -> bool:
    status_code = getattr(error, "status_code", None)
    code = getattr(error, "code", None)
    message = str(error).lower()

    return (
        status_code == 429
        or code == 429
        or "resource_exhausted" in message
        or "quota" in message
    )


def ask_llm(prompt: str) -> str:
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise RuntimeError("Missing GEMINI_API_KEY in .env")

    client = genai.Client(api_key=api_key)

    try:
        response = client.models.generate_content(
            model=get_model_name(),
            contents=prompt,
        )
    except Exception as error:
        if _is_quota_error(error):
            raise RuntimeError(
                "Gemini quota was exceeded. Try again later, try a different "
                "free-tier GEMINI_MODEL, or use --dry-run to test without API calls."
            ) from None
        raise

    return response.text
