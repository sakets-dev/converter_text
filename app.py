from flask import Flask, request, render_template
import pytesseract
from PIL import Image
import pdfplumber
from pdf2image import convert_from_path
import os

app = Flask(__name__)

def extract_text_from_image(image_path):
    image = Image.open(image_path)
    return pytesseract.image_to_string(image)

def extract_text_from_pdf(pdf_path):
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text
            else:
                for image in convert_from_path(pdf_path):
                    text += pytesseract.image_to_string(image)
    return text

@app.route("/", methods=["GET", "POST"])
def upload_file():
    text = None
    if request.method == "POST":
        f = request.files["file"]
        path = f.filename
        f.save(path)
        ext = os.path.splitext(path)[1].lower()
        text = extract_text_from_image(path) if ext in [".jpg", ".jpeg", ".png"] else extract_text_from_pdf(path)
        os.remove(path)
    return render_template("index.html", text=text)

if __name__ == "__main__":
    app.run(debug=True)
