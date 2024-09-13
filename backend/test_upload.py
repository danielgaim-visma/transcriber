import requests
import os


def test_upload(file_path):
    url = "http://127.0.0.1:5000/meetings/upload"

    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return

    with open(file_path, 'rb') as file:
        files = {'file': file}
        try:
            response = requests.post(url, files=files)
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.text}")
        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")


# Replace with your actual file name
file_name = "your_audio_file.wav"
file_path = f"/Users/daniel.gaimvisma.com/Downloads/{file_name}"

test_upload(file_path)