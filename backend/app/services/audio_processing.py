import os
from flask import current_app
import traceback
from google.oauth2 import service_account
from google.cloud import speech, storage
from pydub import AudioSegment
import io

# Directly specify the path to your credentials file
CREDENTIALS_PATH = "/Users/daniel.gaimvisma.com/Downloads/test-flyta-cm-c0d5ab00c3ec.json"

# Load credentials
credentials = service_account.Credentials.from_service_account_file(CREDENTIALS_PATH)


def convert_to_mono_wav(file_path):
    try:
        audio = AudioSegment.from_file(file_path)
        if audio.channels > 1:
            audio = audio.set_channels(1)

        # Convert to 16kHz sample rate
        audio = audio.set_frame_rate(16000)

        mono_wav_path = os.path.splitext(file_path)[0] + '_mono.wav'
        audio.export(mono_wav_path, format="wav")

        current_app.logger.info(f"Converted {file_path} to mono WAV: {mono_wav_path}")
        return mono_wav_path
    except Exception as e:
        current_app.logger.error(f"Error converting audio to mono WAV: {str(e)}")
        current_app.logger.error(traceback.format_exc())
        raise


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
        response = operation.result(timeout=180)

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
        audio = AudioSegment.from_file(file_path)
        current_app.logger.info(f"Audio file properties:")
        current_app.logger.info(f"Channels: {audio.channels}")
        current_app.logger.info(f"Sample width: {audio.sample_width} bytes")
        current_app.logger.info(f"Frame rate: {audio.frame_rate} Hz")
        current_app.logger.info(f"Duration: {len(audio) / 1000:.2f} seconds")
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

        # Convert to mono WAV
        mono_wav_path = convert_to_mono_wav(file_path)

        # Upload to Google Cloud Storage
        gcs_uri = upload_to_gcs(mono_wav_path, current_app.config['BUCKET_NAME'])
        current_app.logger.info(f"Uploaded to GCS: {gcs_uri}")

        # Transcribe the audio
        transcript = transcribe_audio(gcs_uri)
        current_app.logger.info("Transcription completed")

        # Clean up temporary mono WAV file
        os.remove(mono_wav_path)

        return transcript
    except Exception as e:
        current_app.logger.error(f"Error processing audio file: {str(e)}")
        current_app.logger.error(traceback.format_exc())
        return None