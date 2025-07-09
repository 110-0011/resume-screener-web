from flask import Flask, render_template, request
import os
import fitz  # PyMuPDF

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Create upload folder if not exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

KEYWORDS = ['python', 'machine learning', 'internship', 'cgpa', 'data science']

def extract_text_from_pdf(pdf_path):
    text = ""
    doc = fitz.open(pdf_path)
    for page in doc:
        text += page.get_text()
    return text

def score_resume(text, keywords):
    score = 0
    for word in keywords:
        if word.lower() in text.lower():
            score += 1
    return score

@app.route('/', methods=['GET', 'POST'])
def index():
    results = []

    if request.method == 'POST':
        files = request.files.getlist('resumes')

        for file in files:
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filepath)
            text = extract_text_from_pdf(filepath)
            score = score_resume(text, KEYWORDS)
            results.append({'name': file.filename, 'score': score})

        results = sorted(results, key=lambda x: x['score'], reverse=True)

    return render_template('index.html', results=results)

if __name__ == '__main__':
    app.run(debug=True)
