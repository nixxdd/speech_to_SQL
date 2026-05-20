import requests
import pandas as pd

try:
    response = requests.post(
                "http://localhost:8000/database_query",
                json={
                    'query_text': 'SELECT * FROM users;'
                }
            )

    if response.ok:
        result = response.json()
        print(f'RESULT: {result}\n\n')
        print(f'DataFrame: {pd.DataFrame(result['data'])}')
    else:
        print(f'Error {response.status_code}: {response.text}')
except Exception as e:
    print(e)