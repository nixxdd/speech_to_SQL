"""
- When calling this module you pass an audio file and which engine to use (Whisper or Speechmatics)
- Whisper runs locally
- Speechmatics connect to their cloud service using an API key and fetches the result
- Return a string containing the transcription of the audio file 
"""

import whisper
from speechmatics.batch import AsyncClient, TranscriptionConfig, OperatingPoint, AuthenticationError
from ..config import settings

def _transcribe_whisper(file_path: str) -> str:
    model = whisper.load_model("turbo")
    result = model.transcribe(file_path)
    return result['text']

async def _transcribe_speechmatics(file_path: str) -> str:
    SPEECHMATICS_API_KEY = settings.SPEECHMATICS_API_KEY

    try:
        # Initialize batch client
        async with AsyncClient(api_key=SPEECHMATICS_API_KEY) as client:
            # Configure transcription
            config = TranscriptionConfig(
                language="en",
                operating_point=OperatingPoint.ENHANCED,
            )

            # Transcribe with batch API
            result = await client.transcribe(
                str(file_path),
                transcription_config=config,
            )

        # Extract and display transcript
        return result.transcript_text 

    except AuthenticationError as e:
        raise ValueError(f"Speechmatics authentication failed: {e}") 
    except Exception as e:
        raise RuntimeError(f"Speechmatics transcription failed: {e}")

async def transcribe_audio(file_path: str, model_name: str) -> str:
    if model_name.lower() == "whisper":
        return _transcribe_whisper(file_path)
    elif model_name.lower() == "speechmatics":
        return await _transcribe_speechmatics(file_path)
    else:
        raise ValueError(f"Unknown model '{model_name}'. Use 'whisper' or 'speechmatics'")
