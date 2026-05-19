"""
PSUDO CODE

- When calling this module you pass an audio file and which engine to use (Whisper or Speechmatics)
- Whisper runs locally
- Speechmatics connect to their cloud service using an API key and fetches the result
- Return a string containing the transcription of the audio file 
"""

import whisper
from speechmatics.batch import AsyncClient, TranscriptionConfig, OperatingPoint, AuthenticationError
import asyncio
import os
from ..config import settings

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
AUDIO_FOLDER = os.path.join(BASE_DIR, "test_resources", "audio_tests")  

def get_audio_files_path() -> list[str]:
    """
    Returns a list of all audio file paths found in the audio folder.
    """
    supported_formats = (".mp3", ".wav", ".m4a", ".ogg", ".flac")
    
    if not os.path.exists(AUDIO_FOLDER):
        raise RuntimeError(f"Audio folder '{AUDIO_FOLDER}' not found")
    
    return [
        os.path.join(AUDIO_FOLDER, f)
        for f in os.listdir(AUDIO_FOLDER)
        if f.endswith(supported_formats)
    ]

def _transcribe_whisper(file_path: str) -> str:
    model = whisper.load_model("turbo")
    result = model.transcribe(file_path)
    return result['text']

async def _transcribe_speechmatics(file_path: str) -> str:
    SPEECHMATICS_API_KEY = settings.SPEECHMATICS_API_KEY

    try:
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
        transcript = result.transcript_text
        print("Full transcript:")
        print(f'"{transcript}"')
    except( AuthenticationError, ValueError) as e:
        print(f"\nAuthentication Error: {e}")

def transcribe_audio(file_path: str, model_name: str) -> str:
    if model_name.lower() == "whisper":
        return _transcribe_whisper(file_path)
    elif model_name.lower() == "speechmatics":
        # speechmatics logic
        pass
    else:
        raise ValueError(f"Unknown model '{model_name}'. Use 'whisper' or 'speechmatics'")

#def __main__():
#    transcribe_audio(file_path=r"C:\Users\marco\Desktop\speech_to_sql_project\backend\modules\test_resources\audio_tests\q1.wav")

print('speech_to_text_module START')
print(f'AUDIO FOLDER PATH: {AUDIO_FOLDER}')
#__main__()
print('OK')