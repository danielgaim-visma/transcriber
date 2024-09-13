from openai import OpenAI
from flask import current_app
import os

def summarize_transcript(transcript):
    try:
        # Initialize the OpenAI client
        client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

        # Prepare the prompt for GPT-4
        prompt = f"Please summarize the following transcript:\n\n{transcript}\n\nSummary:"

        # Call the OpenAI API
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that summarizes meeting transcripts."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=150  # Adjust this value based on how long you want the summary to be
        )

        # Extract the summary from the response
        summary = response.choices[0].message.content.strip()

        current_app.logger.info("Transcript summarization completed successfully")
        return summary

    except Exception as e:
        current_app.logger.error(f"Error summarizing transcript: {str(e)}")
        return None