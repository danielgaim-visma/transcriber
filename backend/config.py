import os

# Base directory of the application
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Upload folder path
UPLOAD_FOLDER = '/Users/daniel.gaimvisma.com/PycharmProjects/pythonProject4/backend/app/Upload'

# Ensure the upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {'wav', 'mp3', 'flac'}

# Google Cloud Storage bucket name
BUCKET_NAME =

# Other configuration settings...
SECRET_KEY = 'your-secret-key-here'  # Replace with a real secret key
DEBUG = True  # Set to False in production

# Google Cloud credentials path
GOOGLE_APPLICATION_CREDENTIALS =

# OpenAI API key
OPENAI_API_KEY =