import subprocess
import requests

def check_ffmpeg():
    try:
        subprocess.run(["ffmpeg", "-version"], 
                    capture_output=True, 
                    check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def check_speechmatics_api(key):
    # response = requests.get("http://localhost:8000/check_speechmatics", params={"api_key": key})
    # print(response)
    # return response.json()

    response = requests.get(
        "https://asr.api.speechmatics.com/v2/jobs/",
        headers={"Authorization": f"Bearer {key}"}
    )
    return response.status_code == 200