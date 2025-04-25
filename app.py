from flask import Flask, request, jsonify
from Form_LLM import get_previous_forms,generate_autofill,generate_compliance_report,RFI_Suggestion,speechtotext,generate_project_insights,ImageProcessing
import os
from werkzeug.utils import secure_filename
app = Flask(__name__)

@app.route("/autofill", methods=["POST"])
def autofill():
    data = request.json
    # user_id = data.get("user_id")
    form_type = data.get("form_type")
    url="https://hrb5wx2v-8000.inc1.devtunnels.ms/api/data"

    if not form_type :
        return jsonify({"error": "form_type required"}), 400

    previous_forms = get_previous_forms(url)
    ai_suggestion = generate_autofill(form_type, previous_forms)
    
    return jsonify({
        "form_type": form_type,
        "suggested_data": ai_suggestion
    })

@app.route("/complinces_standards", methods= ["POST"])
def compliences():
    data=request.json
    # user_id=data.get("user_id")
    site_report_text=data.get("report_text")

    if not site_report_text:
        return jsonify({"error" : "user_id and report_text required"})
    standard_response=generate_compliance_report(site_report_text)

    return jsonify({
        "ai_report": standard_response
    })
    

#rfi suggestion ##
@app.route("/rfi_suggestions", methods= ["POST"])
def rfi():
    data=request.json
    # user_id=data.get("user_id")
    rfi_question=data.get("question")
    # api_url=data.get("url")

    if not rfi_question:
        return jsonify({"error" : "report_text required"})
    
    standard_response= RFI_Suggestion(rfi_question)

    return jsonify({
        "rfi_suggestion": standard_response
    })
    


@app.route("/speechtotext", methods=["POST"])
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
        # Call your function
        transcript = speechtotext(file_path)
        return jsonify({"transcription": transcript})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        # Clean up file
        if os.path.exists(file_path):
            os.remove(file_path)


@app.route("/project_insights", methods=["POST"])
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


# --- Image Processing Route ---
@app.route("/analyze_image", methods=["POST"])
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