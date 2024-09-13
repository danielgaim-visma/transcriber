from flask import Blueprint, request, jsonify, current_app
import os
from werkzeug.utils import secure_filename
from ..services.audio_processing import process_audio_file
import traceback

meetings = Blueprint('meetings', __name__)

@meetings.route('/upload', methods=['POST'])
def upload_file():
    current_app.logger.info("Received upload request")
    current_app.logger.debug(f"Request method: {request.method}")
    current_app.logger.debug(f"Files in request: {request.files}")

    if 'file' not in request.files:
        current_app.logger.warning("No file part in the request")
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        current_app.logger.warning("No selected file")
        return jsonify({'error': 'No selected file'}), 400

    if file and allowed_file(file.filename):
        try:
            filename = secure_filename(file.filename)
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            current_app.logger.info(f"File saved to {file_path}")

            transcript = process_audio_file(file_path)

            if transcript:
                current_app.logger.info("Transcription successful")
                return jsonify({'transcript': transcript}), 200
            else:
                current_app.logger.warning("Transcription failed")
                return jsonify({'error': 'Transcription failed'}), 500
        except Exception as e:
            current_app.logger.error(f"Error processing file: {str(e)}")
            current_app.logger.error(traceback.format_exc())
            return jsonify({'error': 'Internal server error'}), 500

    current_app.logger.warning("Invalid file type")
    return jsonify({'error': 'File type not allowed'}), 400

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']