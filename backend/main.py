from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from sqlalchemy import text
from pydantic import BaseModel
import tempfile
import shutil
import os

from backend.modules.db_module import get_db, select_query
from backend.modules.wrenai_module import generate_sql
from backend.modules.speech_to_text_module import transcribe_audio

class QueryRequest(BaseModel):
    query_text: str
    params: dict = {}

class QuestionRequest(BaseModel):
    question: str

app = FastAPI()

@app.get("/")
def root():
    return {"message": "FastAPI app is running"}

@app.post("/transcribe")
async def transcribe(file: UploadFile = File(...), engine: str = Form(...)):
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            shutil.copyfileobj(file.file, tmp)
            tmp_path = tmp.name

        result = transcribe_audio(file_path=tmp_path, engine=engine)
        return {'status': 'success', 'engine': engine, 'transcription': result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        os.remove(tmp_path)

# TEST ENDPOINT
@app.get("/get_audio")
def get_audio_files():
    return {"status": "success", "data": get_audio_files()}

@app.post('/database_query')
def run_database_query(request: QueryRequest, db: Session = Depends(get_db)):
    """
    Run a query in the database
    """
    try:
        result = select_query(db, request.query_text, request.params)
        return {"status": "Success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate_sql")
def generate_sql_with_wrenai(request: QuestionRequest):
    try:
        result = generate_sql(request.question)
        return {"status": "success", "data": result}
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
