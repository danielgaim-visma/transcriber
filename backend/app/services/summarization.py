from openai import OpenAI
from flask import current_app

def generate_meeting_minutes(transcript):
    try:
        # Initialize the OpenAI client
        client = OpenAI(api_key=current_app.config['OPENAI_API_KEY'])

        # Prepare the system message with detailed instructions
        system_message = """
        You are an AI assistant tasked with generating comprehensive meeting minutes from a transcript. Follow these instructions:

        1. Extract Participant Details:
           - Identify all participants, including their roles and titles, from the transcript.

        2. Determine Meeting Purpose:
           - Extract the key reason or objective of the meeting from the initial dialogue or as stated by the chairperson.

        3. Identify Key Discussion Points:
           - Break down the transcript into sections based on different speakers or topics.
           - Capture the essence of what each participant says, focusing on decisions, action items, and key opinions.

        4. Action Items and Assignments:
           - Identify any tasks or follow-ups assigned during the meeting.
           - Note the responsible party next to each action item.

        5. Proposals and Decisions:
           - Highlight any new proposals, strategies, or decisions agreed upon during the meeting.

        6. Closing Remarks:
           - Note any concluding statements or summaries provided by the meeting chairperson.
           - Include any scheduled follow-up or next meeting date if mentioned.

        7. Formatting and Organization:
           - Organize the extracted information into a clear, readable format.
           - Use bullet points for discussion items and numbered lists for action items.
           - Ensure consistency in tense and voice throughout the document.

        8. Review and Edit:
           - Ensure accuracy and completeness of the minutes.
           - Check for grammatical errors and adjust the language for formal presentation.

        Generate the meeting minutes based on these instructions, maintaining a professional and concise tone throughout. Use Markdown formatting for better readability.
        """

        # Prepare the user message with the transcript
        user_message = f"Here's the transcript of the meeting. Please generate detailed meeting minutes based on the provided instructions:\n\n{transcript}"

        # Call the OpenAI API
        response = client.chat.completions.create(
            model="gpt-4o-2024-05-13",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message}
            ],
            max_tokens=4000
        )

        # Extract the meeting minutes from the response
        meeting_minutes = response.choices[0].message.content.strip()

        current_app.logger.info("Meeting minutes generation completed successfully")
        return meeting_minutes

    except Exception as e:
        current_app.logger.error(f"Error generating meeting minutes: {str(e)}")
        return None