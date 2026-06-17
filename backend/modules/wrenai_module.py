from fastapi import HTTPException
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

def run_sql(sql_query: str) -> dict:
    url = f"{settings.WREN_AI_BASE_URL}/api/v1/run_sql"
    payload = {"sql": sql_query}
    try:
        with httpx.Client(timeout=60) as client:
            response = client.post(url, json=payload)            
            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail="Failed to run query")
            return response.json()

    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail=f"Service unavailable: {str(e)}")
