from flask import Flask, request, render_template_string
import pytesseract
from PIL import Image
import pdfplumber
import os
from pdf2image import convert_from_path

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
                # OCR for scanned PDFs
                for image in convert_from_path(pdf_path):
                    text += pytesseract.image_to_string(image)
    return text

def convert_to_text(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    if ext in ['.jpg', '.jpeg', '.png']:
        return extract_text_from_image(file_path)
    elif ext == '.pdf':
        return extract_text_from_pdf(file_path)
    else:
        return "Unsupported file type."

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    html = '''
    <h2>Upload PDF or Image to Extract Text</h2>
    <form method="POST" enctype="multipart/form-data">
      <input type="file" name="file" required>
      <button type="submit">Convert</button>
    </form>
    {% if text %}
    <h3>Extracted Text:</h3>
    <pre>{{ text }}</pre>
    {% endif %}
    '''
    text = None
    if request.method == 'POST':
        f = request.files['file']
        path = f.filename
        f.save(path)
        text = convert_to_text(path)
        os.remove(path)
    return render_template_string(html, text=text)

if __name__ == '__main__':
    app.run(debug=True)
