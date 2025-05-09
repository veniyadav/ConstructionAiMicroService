from langchain.prompts import ChatPromptTemplate,PromptTemplate
from groq import Groq
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
import re
from utiles.globalllm import GroqLLM
import json 
from form_schemas import form_schemas , compliance_json_template # your schema map
from utiles.utils import load_retriever_from_faiss ,fetch_rfi_data_from_api,format_rfi_history,encode_image,load_retriever_from_faiss_projects #getProject,formatProjects
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("MY_API_KEY")
client = Groq(api_key=API_KEY)

groq_llm = GroqLLM(model="llama-3.1-8b-instant", api_key=API_KEY,temperature=0.4)

# FORM Auto suggest part #
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
    elif form_type == 'rfis':
        forms = data.get('rfis', [])
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



    chain = prompt | groq_llm
    response = chain.invoke({})  # Invoke the chain with no additional input

  # Clean and parse the JSON response

    match = re.search(r"```json\n(.*)\n```", response, re.DOTALL)
    if match:
        json_str = match.group(1)
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            return {"error": "Failed to parse AI response as JSON", "raw_output": json_str}
    else:
        return {"error": "No valid JSON block found", "raw_output": response}
    

# Compliance report part

def generate_compliance_report(site_report_text):
    retriever = load_retriever_from_faiss(jsonpath="australian_standards.json", index_path="faiss_index")

    # Retrieve relevant standard documents
    retrieved_docs = retriever.get_relevant_documents(site_report_text)
    standards_summary = "\n".join([doc.page_content for doc in retrieved_docs])

    # Escape curly braces in the JSON schema
    escaped_format = compliance_json_template.replace("{", "{{").replace("}", "}}").strip()

        # Define a safe prompt template with a single string input
    template = """
    You are an Australian safety compliance expert.

    Your task is to analyze a site report and determine if there are any compliance issues with reference to the following Australian Standards:

    {standards_summary}

    Respond ONLY in the following JSON format:
    ```json
    {escaped_format}"""

    prompt = PromptTemplate(
        input_variables=["standards_summary", "site_report_text", "escaped_format"],
        template=template,
    )

    # Run the LLMChain
    chain = LLMChain(llm=groq_llm, prompt=prompt)
    response = chain.run({
        "standards_summary": standards_summary,
        "site_report_text": site_report_text,
        "escaped_format": escaped_format,
    })

    # Extract JSON from LLM output
    match = re.search(r"```json\n(.*)\n```", response, re.DOTALL)
    if match:
        json_str = match.group(1)
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            return {
                "error": "Failed to parse AI response as JSON",
                "raw_output": json_str
            }
    else:
        return {
            "error": "No valid JSON block found",
            "raw_output": response
        }

##RFI ###

def RFI_Suggestion(user_rfi_question):  #api url when extract data 
    api="https://construction-backend-production-d7ac.up.railway.app/api/rfi"
    rfi_entries = fetch_rfi_data_from_api(api_url=api)
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


    # chain = prompt | llm
    chain = prompt | groq_llm
    response = chain.invoke({})
    return response




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
        #for summery

        system_message = f"""summarize the following text in a concise manner, highlighting key points and important details."""

    # Use LangChain's ChatPromptTemplate
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_message.strip()),
        ("human", f"Summarize the following text:\n{data}")
    ])



    chain = prompt | groq_llm
    response = chain.invoke({})  # Invoke the chain with no additional input
    return data ,response #transcription.text, transcription.segments[0].words[0].start_time, transcription.segments[0].words[-1].end_time, transcription.segments[0].words[0].word, transcription.segments[0].words[-1].word

#GET PROJESTS INSITES  ChatBOt#
def generate_project_insights(user_query, user_id):
    retriever = load_retriever_from_faiss_projects(jsonpath="Database.json", index_path="faiss_index2")

    # Retrieve relevant documents based on the full document similarity (not specific keys)
    retrieved_docs = retriever.get_relevant_documents(user_query)

    # Construct a summary of the retrieved documents
    standards_summary = "\n".join([doc.page_content for doc in retrieved_docs]) if retrieved_docs else ""

    # Define a single template with rules
    template = """
    You are an AI assistant for a construction project. Your task is to provide the user with the **exact information** they request, based on the data available. If the information is found in the database, return that directly. If not, **never say no**, and always search the web to provide the most relevant and accurate answer.

    Here are the rules:
    1. If relevant information is found in the database, provide the answer directly.
    2. If no relevant information is found in the database, search the web and provide a direct, concise, and accurate answer.
    3. Do **not** provide any greetings, extra context, or introductory information. Just answer the question directly.
    4. **Never say no**. If data is not available in the database, proceed to search the internet for the most relevant information and provide it.
    5. Only answer precise and short don't add more irrelevent information 

    The user's question is: "{user_query}"

    Here is the relevant data from the database (if available):
    {standards_summary}

    Please answer the user's question directly and concisely. If relevant information is not available in the database, search the internet and provide the answer.
    """

    # Create the prompt template
    prompt = PromptTemplate(
        input_variables=["standards_summary", "user_query"],
        template=template,
    )

    # Run the LLMChain
    chain = LLMChain(llm=groq_llm, prompt=prompt)

    # Generate the response using the retrieved documents and user query
    response = chain.run({
        "standards_summary": standards_summary,
        "user_query": user_query,
    })

    return response

#image classification of construction site     

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
