from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate
from groq import Groq
import os
import re
import base64
import json 
import requests
from form_schemas import form_schemas , compliance_json_template # your schema map
API_KEY = "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"
client = Groq(api_key=API_KEY)

# FORM Auto suggest part #

import requests

def get_previous_forms(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Will raise an HTTPError for bad responses

        # Try to parse JSON
        data = response.json()
        print("Fetched data:", data)
        return data

    except requests.exceptions.HTTPError as http_err:
        print(f"[HTTP ERROR] {http_err} - Status Code: {response.status_code}")
        print("Response text:", response.text[:500])  # Avoid printing a giant HTML dump

    except requests.exceptions.JSONDecodeError as json_err:
        print(f"[JSON ERROR] Failed to decode JSON: {json_err}")
        print("Response text:", response.text[:500])

    except Exception as err:
        print(f"[ERROR] Unexpected error: {err}")

    return None  # Always return something, even on failure


# def generate_autofill(form_type, previous_forms):
    # Combine previous data into a prompt
    schema = form_schemas.get(form_type)
    if not schema:
        return f"Unsupported form type: {form_type}"
    
    escaped_schema = schema.replace("{", "{{").replace("}", "}}")
    

    # system_message = f"You are a helpful assistant that fills out {form_type} forms based on user history " # below.\n\n{history}
    

    # System prompt
    system_message = f"""
        You are a helpful assistant that fills out SWMS forms in JSON format.
        Based on previous form data and the current request, suggest an auto-filled form {form_type} forms based on user history.

        ONLY return a JSON object that matches this schema:
        ```json
        {escaped_schema}
        """
    
    # Use LangChain's ChatPromptTemplate
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_message),
        ("human", f"Based on the following past forms:\n{previous_forms}\n\nGenerate a new autofilled form.")
    ])

    # messages.append(("human", data["human_message"]))

    llm = ChatGroq(
        model="llama-3.1-8b-instant",
        api_key=API_KEY,
        temperature=0,
        max_tokens=None,
        timeout=None,
        max_retries=2,
    )
    
    chain = prompt | llm
    response = chain.invoke({})
    return response.content

def generate_autofill(form_type, previous_forms):
    # Ensure we're accessing the 'data' field correctly, which is a dictionary containing lists
    data = previous_forms.get('data', {})

    # Choose the correct list based on your form type, e.g., 'swms', 'incidents', or 'itps'
    if form_type == 'swms':
        forms = data.get('swms', [])
    elif form_type == 'incidents':
        forms = data.get('incidents', [])
    elif form_type == 'itps':
        forms = data.get('itps', [])
    else:
        return f"Unsupported form type: {form_type}"

    # Combine previous data into a prompt, ensuring we handle the forms correctly
    history = "\n\n".join([f"Form {i+1}: {form.get('description', 'No description')}" for i, form in enumerate(forms)])

    # Fetch schema for the specified form_type
    schema = form_schemas.get(form_type)
    if not schema:
        return f"Unsupported form type: {form_type}"

    # Escape curly braces for the schema, as required by LangChain
    escaped_schema = schema.replace("{", "{{").replace("}", "}}")

    # System message for LangChain prompt
    system_message = f"""
        You are a helpful assistant that fills out {form_type} forms in JSON format.
        Based on previous form data and the current request, suggest an auto-filled form {form_type}.
        
        RULE:
        1. Don't use this previous word rather than provide the information from past forms

        ONLY return a JSON object that matches this schema:
        ```json
        {escaped_schema}
        ```
    """

    # Use LangChain's ChatPromptTemplate
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_message.strip()),
        ("human", f"Based on the following past forms:\n{history}\n\nGenerate and suggest new autofilled form.")
    ])

    # Initialize the LLM (ChatGroq in your case)
    llm = ChatGroq(
        model="llama-3.1-8b-instant",
        api_key=API_KEY,
        temperature=0,
        max_tokens=None,
        timeout=None,
        max_retries=2,
    )

    # Chain the prompt with the LLM
    chain = prompt | llm
    response = chain.invoke({})  # Invoke the chain with no additional input

  # 🔍 Clean and parse the JSON response

    match = re.search(r"```json\n(.*)\n```", response.content, re.DOTALL)
    if match:
        json_str = match.group(1)
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            return {"error": "Failed to parse AI response as JSON", "raw_output": json_str}
    else:
        return {"error": "No valid JSON block found", "raw_output": response.content}

#for  AI-Generated Compliance & Rectification Reports – AI cross-checks Australian Standerds and provides fixes #


import json

def load_standards_summary(file_path="australian_standards.json"):
    with open(file_path, "r") as f:
        standards = json.load(f)

    formatted = ""
    for s in standards:
        formatted += f"- {s['standard']} – {s['section']}: {s['description']}\n"
    
    return formatted.strip()


def generate_compliance_report(site_report_text):

    standards_summary = load_standards_summary()

    # Escape curly braces
    escaped_format = compliance_json_template.replace("{", "{{").replace("}", "}}")

    system_prompt = f"""
    You are an Australian safety compliance expert.

    Your task is to analyze a site report and determine if there are any compliance issues with reference to the following Australian Standards:

    {standards_summary}

    Respond ONLY in the following JSON format:
    ```json
    {escaped_format}"""

    prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt.strip()),
    ("human", f"Site Report: {site_report_text}")
    ])

    llm = ChatGroq(
        model="llama-3.1-8b-instant",
        api_key=API_KEY,
        temperature=0,
        max_tokens=None,
        timeout=None,
        max_retries=2,
    )

    chain = prompt | llm
    response = chain.invoke({})
    match = re.search(r"```json\n(.*)\n```", response.content, re.DOTALL)
    if match:
        json_str = match.group(1)
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            return {"error": "Failed to parse AI response as JSON", "raw_output": json_str}
    else:
        return {"error": "No valid JSON block found", "raw_output": response.content}

##RFI ###

def fetch_rfi_data_from_api(api_url):
    try:
        response = requests.get(api_url)
        response.raise_for_status()  # Raise error for bad status
        print(response.json())
        return response.json()  
    
    # Assumes the API returns JSON
    except requests.RequestException as e:
        print(f"Error fetching RFI data: {e}")
        return []

def format_rfi_history(rfi_entries):
    formatted = ""
    for i, rfi in enumerate(rfi_entries, 1):
        if not isinstance(rfi, dict):
            print(f"Skipping invalid RFI entry at index {i}: {rfi}")
            continue

        question = rfi.get('question') or rfi.get('rfi_question')
        answer = rfi.get('answer') or rfi.get('rfi_answer')
        formatted += f"RFI {i}:\nQ: {question}\nA: {answer}\n\n"
    return formatted.strip()


def RFI_Suggestion(user_rfi_question):  #api url when extract data 
    # api="https://hrb5wx2v-8000.inc1.devtunnels.ms/api/data"
    api="https://hrb5wx2v-8000.inc1.devtunnels.ms/api/rfi"
    rfi_entries = fetch_rfi_data_from_api(api_url=api)

    # Debugging: Print the fetched RFI entries
    print("Fetched RFI Entries:", rfi_entries)

    history = format_rfi_history(rfi_entries)

    system_prompt = f"""
You are a construction project assistant. Your job is to suggest answers to new RFIs by looking at historical RFI data.

Here is the history of past RFIs and their answers:
{history}

Now, generate a helpful response to the following new RFI. Do not invent data — only infer from what’s available.
Return the answer ONLY as plain text.
"""

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt.strip()),
        ("human", user_rfi_question)
    ])

    llm = ChatGroq(
        model="llama-3.1-8b-instant",
        api_key=API_KEY,
        temperature=0.3,
    )

    chain = prompt | llm
    response = chain.invoke({})
    return response.content




# Speech to text 
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

#GET PROJESTS INSITES #
def getProject(api_url):
    try:
        response = requests.get(api_url)
        response.raise_for_status()  # Raise error for bad status
        print(response.json)
        return response.json()  # Assumes the API returns JSON
    except requests.RequestException as e:
        print(f"Error fetching PROJECTdata: {e}")
        return []

def formatProjects(rfi_entries):
    formatted = ""
    for i, rfi in enumerate(rfi_entries, 1):
        question = rfi.get('question') or rfi.get('rfi_question')
        answer = rfi.get('answer') or rfi.get('rfi_answer')
        formatted += f"RFI {i}:\nQ: {question}\nA: {answer}\n\n"
    return formatted.strip()

def generate_project_insights(user_query,user_id):
    """
    Uses AI to generate insights or alerts from construction project data.
    project_data: List of dicts (e.g., rows from a spreadsheet)
    """

    api=f"https://xt2cpwt7-8000.inc1.devtunnels.ms/api/projects/by-user/{user_id}"
    
    # Convert project data to readable format
    prdata=getProject(api_url=api)
    project_data=formatProjects(prdata)

    context = "\n".join([f"- {json.dumps(row)}" for row in project_data])

    system_prompt = f"""
You are a smart AI assistant for a construction project.

Your job is to analyze project data and answer user queries. 
You may highlight risks, delays, compliance issues, or general updates.

Project Context:
{context}

Always provide clear and concise construction insights in bullet points or paragraphs.
"""

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt.strip()),
        ("human", user_query)
    ])

    llm = ChatGroq(
        model="llama-3.1-8b-instant",
        api_key=API_KEY,
        temperature=0.3,
    )

    chain = prompt | llm
    response = chain.invoke({})
    return response.content


#image classification of constructio
def encode_image(image_path):
  if not os.path.exists(image_path):
    raise FileNotFoundError(f"The file '{image_path}' does not exist.")
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')

# Path to your image
def ImageProcessing(imagepath):
    # Getting the base64 string
    base64_image = encode_image(image_path=imagepath)

    client = Groq(api_key="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")

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": """Analyze this image for any visible construction-related issues or failures,
                such as cracks in walls, broken wires, pipe leakages, sewage overflows, or structural damage. 
                Clearly identify each detected problem, describe its location in the image, and provide a brief 
                explanation of the cause. Then, suggest practical repair methods and list safety measures that 
                should be taken during inspection and repair.."""            
            },

            
            
            {
                "role": "user",
                "content": [
                {
                    "type": "text",
                    "text": "Please analyze this image and report any issues with suggestions."
                },
                {
                    "type": "image_url",
                    "image_url": {
                    "url": f"data:image/jpeg;base64,{base64_image}"
                    }
                }
                ]
            }
            ],
        model="meta-llama/llama-4-scout-17b-16e-instruct",
    )
    return chat_completion.choices[0].message.content



# if __name__ == "__main__":
#     form_type = "ITP"
#     previous_forms = [
#         {"data": "Hazard: Working at heights, Control: Safety harness"},
#         {"data": "Hazard: Electrical, Control: Lockout-tagout"},
#     ]
#     # user_input = "Please generate a new SWMS form for a bridge project with common site hazards."

#     suggested_form = generate_autofill(form_type, previous_forms)
#     # print(suggested_form)


#     site_report = "Exposed live wiring hanging in a corridor where workers walk frequently, no signage or protection."
#     result = generate_compliance_report(site_report)
#     # print(result)


#     user_rfi = "What fire rating applies to the corridor walls?"
#     response = RFI_Suggestion(user_rfi)
#     # print("Suggested RFI Response:", response)

#     filename="harvard.wav"
#     text=speechtotext(filename=filename)
#     # print(text)

#     user_query = "What compliance risks should I be aware of this week?"
#     insights = generate_project_insights(user_query)
#     # print(insights)

    
#     image_path = r"image\istockphoto-1306206468-612x612.jpg"
#     text=ImageProcessing(imagepath=image_path)
#     # print(text)