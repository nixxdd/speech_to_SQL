import httpx
from ..config import settings

def generate_sql(question: str) -> dict:
    """
    Sends a question to WrenAI and returns the generated SQL response.
    
    :param question: Natural language question to convert to SQL
    """
    url = f"{settings.WREN_AI_BASE_URL}/api/v1/generate_sql"
    payload = {"question": question}

    try:
        with httpx.Client(timeout=60) as client:
            response = client.post(url, json=payload)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as e:
        raise RuntimeError(f"WrenAI returned an error: {e.response.status_code} - {e.response.text}")
    except httpx.RequestError as e:
        raise RuntimeError(f"Failed to reach WrenAI: {str(e)}")