from google.cloud import speech
from google.cloud import storage
import os
from flask import current_app
import traceback
from google.oauth2 import service_account
import wave

# Directly specify the path to your credentials file
CREDENTIALS_PATH = "/Users/daniel.gaimvisma.com/Downloads/test-flyta-cm-c0d5ab00c3ec.json"

# Load credentials
credentials = service_account.Credentials.from_service_account_file(CREDENTIALS_PATH)


def upload_to_gcs(file_path, bucket_name):
    try:
        storage_client = storage.Client(credentials=credentials)
        bucket = storage_client.get_bucket(bucket_name)
        blob = bucket.blob(os.path.basename(file_path))
        blob.upload_from_filename(file_path)
        return f"gs://{bucket_name}/{blob.name}"
    except Exception as e:
        current_app.logger.error(f"Error uploading to GCS: {str(e)}")
        current_app.logger.error(traceback.format_exc())
        raise


def transcribe_audio(gcs_uri):
    try:
        client = speech.SpeechClient(credentials=credentials)
        audio = speech.RecognitionAudio(uri=gcs_uri)
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            language_code="en-US",
            diarization_config=speech.SpeakerDiarizationConfig(
                enable_speaker_diarization=True,
                min_speaker_count=2,
                max_speaker_count=2,
            ),
        )
        current_app.logger.info(f"Sending transcription request for {gcs_uri}")
        operation = client.long_running_recognize(config=config, audio=audio)
        current_app.logger.info("Waiting for operation to complete...")
        response = operation.result(timeout=90)

        transcript = ""
        for result in response.results:
            current_app.logger.info(f"Transcription: {result.alternatives[0].transcript}")
            transcript += result.alternatives[0].transcript + " "

        return transcript
    except Exception as e:
        current_app.logger.error(f"Error transcribing audio: {str(e)}")
        current_app.logger.error(traceback.format_exc())
        raise


def check_audio_file(file_path):
    try:
        with wave.open(file_path, 'rb') as wav_file:
            channels = wav_file.getnchannels()
            sample_width = wav_file.getsampwidth()
            frame_rate = wav_file.getframerate()
            frames = wav_file.getnframes()
            duration = frames / float(frame_rate)

            current_app.logger.info(f"Audio file properties:")
            current_app.logger.info(f"Channels: {channels}")
            current_app.logger.info(f"Sample width: {sample_width} bytes")
            current_app.logger.info(f"Frame rate: {frame_rate} Hz")
            current_app.logger.info(f"Number of frames: {frames}")
            current_app.logger.info(f"Duration: {duration:.2f} seconds")
    except Exception as e:
        current_app.logger.error(f"Error checking audio file: {str(e)}")
        current_app.logger.error(traceback.format_exc())


def process_audio_file(file_path):
    current_app.logger.info(f"Processing audio file: {file_path}")

    if not os.path.exists(file_path):
        current_app.logger.error(f"File not found: {file_path}")
        return None

    try:
        # Check audio file properties
        check_audio_file(file_path)

        # Upload to Google Cloud Storage
        gcs_uri = upload_to_gcs(file_path, current_app.config['BUCKET_NAME'])
        current_app.logger.info(f"Uploaded to GCS: {gcs_uri}")

        # Transcribe the audio
        transcript = transcribe_audio(gcs_uri)
        current_app.logger.info("Transcription completed")

        return transcript
    except Exception as e:
        current_app.logger.error(f"Error processing audio file: {str(e)}")
        current_app.logger.error(traceback.format_exc())
        return None