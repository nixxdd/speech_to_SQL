from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from sqlalchemy import text
from pydantic import BaseModel
import tempfile
import shutil
import os

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
import logging


from .modules.db_module import get_db, select_query
from .modules.wrenai_module import generate_sql, run_sql
from .modules.speech_to_text_module import transcribe_audio

from .config import settings

class QuestionRequest(BaseModel):
    question: str

class QueryRequest(BaseModel):
    sql_query: str

# Setup logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = FastAPI()

@app.get("/")
def root():
    return {"message": "FastAPI app is running"}

@app.get("/store_speechmatics_key")
async def store_speechmatics_key(api_key):
    print(api_key)
    settings.SPEECHMATICS_API_KEY = api_key
    print(settings.SPEECHMATICS_API_KEY, "YOOOOOOOO" )
    return True

@app.get("/get_tables")
async def get_tables():
    query = "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';"
    result = run_sql(query)
    tables = [record["table_name"] for record in result["records"]]
    return tables

@app.post("/transcribe")
async def transcribe(file: UploadFile = File(...), model_name: str = Form(...)):
    try:
        print(f"Received file: {file.filename}, content_type: {file.content_type}, model_name: {model_name}")

        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            shutil.copyfileobj(file.file, tmp)
            tmp_path = tmp.name

        result = await transcribe_audio(file_path=tmp_path, model_name=model_name)
        print(f'Transcription: {result}')
        return {'status': 'success', 'model_name': model_name, 'transcription': result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        os.remove(tmp_path)

@app.post("/generate_sql")
def generate_sql_with_wrenai(request: QuestionRequest):
    try:
        result = generate_sql(request.question)
        print(f'Result raw: {result}')
        return {"status": "success", "data": result['sql']}
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.post("/run_sql")
def execute_sql(request: QueryRequest):
    result = run_sql(request.sql_query)
    return {"records": result["records"], "columns": result["columns"]}


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.error(f"Validation error on {request.url}")
    logger.error(f"Request body: {await request.body()}")
    logger.error(f"Errors: {exc.errors()}")
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors(), "body": str(await request.body())}
    )