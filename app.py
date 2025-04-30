from flask import Flask, request, jsonify
from Form_LLM import generate_autofill,generate_compliance_report,RFI_Suggestion,speechtotext,generate_project_insights,ImageProcessing
import os
from utiles.utils import get_previous_forms
from werkzeug.utils import secure_filename
import requests
import json
from flask_cors import CORS
from flask_cors import cross_origin


app = Flask(__name__)

CORS(app, resources={r"/*": {"origins": "*"}})

@app.route("/autofill", methods=["POST"])
@cross_origin()
def autofill():
    data = request.json
    form_type = data.get("form_type")
    url="https://construction-backend-production-d7ac.up.railway.app/api/data"

    if not form_type :
        return jsonify({"error": "form_type required"}), 400

    previous_forms = get_previous_forms(url)
    ai_suggestion = generate_autofill(form_type, previous_forms)
    
    return jsonify({
        "form_type": form_type,
        "suggested_data": ai_suggestion
    })

@app.route("/complinces_standards", methods= ["POST"])
@cross_origin()
def compliences():
    data=request.json
    site_report_text=data.get("report_text")

    if not site_report_text:
        return jsonify({"error" : "report_text required"})
    standard_response=generate_compliance_report(site_report_text)

    return jsonify({
        "ai_report": standard_response
    })
    

#rfi suggestion ##
@app.route("/rfi_suggestions", methods= ["POST"])
@cross_origin()
def rfi():
    data=request.json
    rfi_question=data.get("question")
    if not rfi_question:
        return jsonify({"error" : "report_text required"})
    
    standard_response= RFI_Suggestion(rfi_question)

    return jsonify({
        "rfi_suggestion": standard_response
    })
    


@app.route("/speechtotext", methods=["POST"])
@cross_origin()
def speech_to_text_api():
    if "audio" not in request.files:
        return jsonify({"error": "No audio file uploaded"}), 400

    audio_file = request.files["audio"]

    if audio_file.filename == "":
        return jsonify({"error": "Empty filename"}), 400

    filename = secure_filename(audio_file.filename)
    file_path = os.path.join("uploads", filename)

    # Save the file temporarily
    os.makedirs("uploads", exist_ok=True)
    audio_file.save(file_path)

    try:
        transcript,summery = speechtotext(file_path)
        return jsonify({"transcription": transcript, "summery":summery})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        # Clean up file after processing
        if os.path.exists(file_path):
            os.remove(file_path)

#projects part
@app.route("/chatbot", methods=["POST"])
@cross_origin()
def project_insights():
    data = request.json
    user_query = data.get("question")
    user_id=data.get("user_id")

    if not user_id or not user_query:
        return jsonify({"error": "question is required"}), 400

    try:
        insights = generate_project_insights(user_query,user_id=user_id)
        return jsonify({"insights": insights})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    



@app.route("/fetch_data", methods=["POST"])
@cross_origin()
def fetch_data():
    data = request.json
    user_id = data.get("user_id")

    if not user_id :
        return jsonify({"error": "user_id required"}), 400

    url = f"https://construction-backend-production-688f.up.railway.app/api/complete/{user_id}"

    try:
        # Send GET request
        response = requests.get(url)

        # Check if the request was successful
        if response.status_code == 200:
            data = response.json()  # Convert response to JSON
            with open("Database.json", "w", encoding='utf-8') as f:
                json.dump(data, f, indent=4)

            print("Data successfully saved to Database.json")
            return jsonify({"message": "Data successfully saved"}), 200
        else:
            # Handle case when the request fails
            print(f"Request failed with status code: {response.status_code}")
            return jsonify({"error": f"Request failed with status code: {response.status_code}"}), 500

    except Exception as e:
        print(f"Error occurred: {str(e)}")
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

# this is the demo commit time

# --- Image Processing Route ---
@app.route("/analyze_image", methods=["POST"])
@cross_origin()
def analyze_image():
    if "image" not in request.files:
        return jsonify({"error": "No image file uploaded"}), 400

    image_file = request.files["image"]

    if image_file.filename == "":
        return jsonify({"error": "Empty filename"}), 400

    filename = secure_filename(image_file.filename)
    file_path = os.path.join("uploads", filename)

    os.makedirs("uploads", exist_ok=True)
    image_file.save(file_path)

    try:
        result = ImageProcessing(file_path)
        return jsonify({"image_analysis": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)


if __name__ == "__main__":
    app.run(debug=True,host="0.0.0.0",port=8001)
