from flask import Flask, request, jsonify, url_for, send_file
from pdf2docx import Converter
import os
import tempfile
import uuid

app = Flask(__name__)

# Ensure the 'docs' folder exists
if not os.path.exists('docs'):
    os.makedirs('docs')

def convert_pdf_to_docx(pdf_path, docx_path):
    cv = Converter(pdf_path)
    cv.convert(docx_path, start=0, end=None)
    cv.close()

@app.route('/convert', methods=['POST'])
def convert():
    if 'pdf' not in request.files:
        return jsonify({"error": "No PDF file provided"}), 400

    pdf_file = request.files['pdf']

    if not pdf_file.filename.endswith('.pdf'):
        return jsonify({"error": "File is not a PDF"}), 400

    with tempfile.TemporaryDirectory() as temp_dir:
        pdf_path = os.path.join(temp_dir, pdf_file.filename)
        pdf_file.save(pdf_path)
        
        # Generate a unique filename for the DOCX
        unique_filename = str(uuid.uuid4()) + ".docx"
        docx_path = os.path.join('docs', unique_filename)

        try:
            convert_pdf_to_docx(pdf_path, docx_path)

            # Generate the download URL
            download_url = url_for('download_file', filename=unique_filename, _external=True)

            return jsonify({
                "message": "Conversion successful",
                "download_url": download_url
            }), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    return send_file(os.path.join('docs', filename), as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
