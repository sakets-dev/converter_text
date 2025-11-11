from flask import Flask, request, render_template, send_file, redirect, url_for
import pytesseract, pdfplumber, os
from PIL import Image
from pdf2image import convert_from_path

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

history = []

def extract_text_from_image(image_path):
    return pytesseract.image_to_string(Image.open(image_path))

def extract_text_from_pdf(pdf_path):
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            text += page_text if page_text else ""
    if not text:
        for img in convert_from_path(pdf_path):
            text += pytesseract.image_to_string(img)
    return text

@app.route("/", methods=["GET", "POST"])
def index():
    global history
    if request.method == "POST":
        f = request.files["file"]
        if not f.filename:
            return redirect(url_for("index"))
        filename = f.filename
        path = os.path.join(UPLOAD_FOLDER, filename)
        f.save(path)
        ext = os.path.splitext(filename)[1].lower()
        text = extract_text_from_image(path) if ext in [".jpg", ".jpeg", ".png"] else extract_text_from_pdf(path)
        history.insert(0, {"filename": filename, "path": path, "text": text})
    return render_template("index.html", history=history)

@app.route("/preview/<filename>")
def preview(filename):
    path = os.path.join(UPLOAD_FOLDER, filename)
    return send_file(path) if os.path.exists(path) else ("File not found", 404)

@app.route("/delete/<int:index>", methods=["POST"])
def delete_file(index):
    global history
    if 0 <= index < len(history):
        item = history.pop(index)
        if os.path.exists(item["path"]):
            os.remove(item["path"])
    return ("", 204)

if __name__ == "__main__":
    app.run(debug=True)
