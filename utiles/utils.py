import json
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
import base64
import os
import requests
from langchain_community.vectorstores import FAISS as LCFAISS
from langchain_community.embeddings import SentenceTransformerEmbeddings
from sentence_transformers import SentenceTransformer
import faiss


##RAG FUncnalities
# build_faiss_index_from_json("standards_corpus.json", "standards_index.faiss")
def build_faiss_index_from_json(json_path: str, index_path: str, model_name: str = "all-MiniLM-L6-v2"):
    with open(json_path, "r",encoding="utf-8") as f:
        data = json.load(f)

    texts = [f"{entry['section']}: {entry['description']}" for entry in data]

    embeddings = SentenceTransformerEmbeddings(model_name=model_name)
    vectorstore = LCFAISS.from_texts(texts, embedding=embeddings)

    # Save full vectorstore (FAISS + metadata)
    vectorstore.save_local(index_path)

    return index_path


from langchain_community.vectorstores import FAISS as LCFAISS

def load_retriever_from_faiss(jsonpath: str, index_path: str, model_name: str = "all-MiniLM-L6-v2"):
    """
    Loads a FAISS index using LangChain and returns a retriever.
    """
    # Build or update the FAISS index and save it to disk
    build_faiss_index_from_json(jsonpath, index_path, model_name)

    # Initialize embedding model
    embeddings = SentenceTransformerEmbeddings(model_name=model_name)

    # Load the index via LangChain, assuming build_faiss_index_from_json used save_local() instead of faiss.write_index
    vectorstore = LCFAISS.load_local(index_path, embeddings, allow_dangerous_deserialization=True)

    return vectorstore.as_retriever()

#utiles for autofill

def get_previous_forms(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Will raise an HTTPError for bad responses

        # Try to parse JSON
        data = response.json()
        # print("Fetched data:", data)
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


#RFI part 


def fetch_rfi_data_from_api(api_url):
    try:
        response = requests.get(api_url)
        response.raise_for_status()  # Raise error for bad status
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

##projects part 
def build_faiss_for_projects(json_path: str, index_path: str, model_name: str = "all-MiniLM-L6-v2"):
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Use the entire document as the text for FAISS indexing
    texts = [json.dumps(entry) for entry in data]  # Store the entire entry as text
    
    embeddings = SentenceTransformerEmbeddings(model_name=model_name)
    vectorstore = LCFAISS.from_texts(texts, embedding=embeddings)

    # Save the FAISS index
    vectorstore.save_local(index_path)

    return index_path

def load_retriever_from_faiss_projects(jsonpath: str, index_path: str, model_name: str = "all-MiniLM-L6-v2"):
    """
    Loads a FAISS index and returns a retriever that searches entire documents.
    """
    # Build or update the FAISS index and save it to disk
    build_faiss_for_projects(jsonpath, index_path, model_name)

    # Initialize the embedding model
    embeddings = SentenceTransformerEmbeddings(model_name=model_name)

    # Load the FAISS index   
    vectorstore = LCFAISS.load_local(index_path, embeddings, allow_dangerous_deserialization=True)

    return vectorstore.as_retriever()


# IMAGE SUMMERY PART   
def encode_image(image_path):
  if not os.path.exists(image_path):
    raise FileNotFoundError(f"The file '{image_path}' does not exist.")
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')
