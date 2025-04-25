import os
import json
from groq import Groq

# Initialize the Groq client
client = Groq(api_key="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")

# Open the audio file
def speechtotext(filename):
    with open(filename, "rb") as file:
        # Create a transcription of the audio file
        transcription = client.audio.transcriptions.create(
        file=file, # Required audio file
        model="whisper-large-v3-turbo", # Required model to use for transcription
        prompt="Specify context or spelling",  # Optional
        response_format="verbose_json",  # Optional
        timestamp_granularities = ["word", "segment"], # Optional (must set response_format to "json" to use and can specify "word", "segment" (default), or both)
        language="en",  # Optional
        temperature=0.0,  # Optional
        
        )
        data=transcription.text
            # To print only the transcription text, you'd use print(transcription.text) (here we're printing the entire transcription object to access timestamps)
    return data