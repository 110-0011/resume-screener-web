from flask import Flask, render_template, request
import os
import fitz  # PyMuPDF
from sentence_transformers import SentenceTransformer, util

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Load sentence transformer model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Example job description
JOB_DESCRIPTION = """
We are looking for candidates with strong skills in Python, Machine Learning, and Data Science. 
Preference will be given to those who have done internships and have a high CGPA.
"""

# added --> begin

import re

# Define a basic skill set to match against
SKILL_KEYWORDS = {
    'python', 'machine learning', 'sql', 'data science', 'pandas',
    'tensorflow', 'keras', 'numpy', 'scikit-learn', 'deep learning',
    'java', 'c++', 'excel', 'power bi', 'tableau', 'nlp'
}

def extract_cgpa(text):
    # Match GPA formats like: CGPA: 8.5, GPA - 9.1/10 etc.
    match = re.search(r'(?:CGPA|GPA)[\s:]*([0-9]\.\d{1,2})', text, re.IGNORECASE)
    if match:
        return float(match.group(1))
    return 'Not found'

def extract_skills(text):
    found = [skill for skill in SKILL_KEYWORDS if re.search(r'\b' + re.escape(skill) + r'\b', text, re.IGNORECASE)]
    return ', '.join(found) if found else 'Not found'

def extract_experience(text):
    if re.search(r'\bintern(ship)?\b', text, re.IGNORECASE):
        return '1+ Internship'
    return 'No Internship'

# added -- end

def extract_text_from_pdf(pdf_path):
    text = ""
    doc = fitz.open(pdf_path)
    for page in doc:
        text += page.get_text()
    return text

def score_with_ai(text, job_description):
    # Encode resume and job description
    embeddings = model.encode([text, job_description], convert_to_tensor=True)
    similarity = util.pytorch_cos_sim(embeddings[0], embeddings[1])
    return float(similarity[0][0]) * 10  # Convert similarity to 0-10 score

@app.route('/', methods=['GET', 'POST'])
def index():
    results = []

    if request.method == 'POST':
        files = request.files.getlist('resumes')

        for file in files:
            if file.filename.endswith('.pdf'):
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
                file.save(filepath)

                text = extract_text_from_pdf(filepath)
                ai_score = score_with_ai(text, JOB_DESCRIPTION)

                # === Simple keyword-based placeholder parsing ===
                # These are mockups – later we can improve with NLP
                """cgpa = 8.2  # TODO: extract from text
                skills = 'Python, SQL'  # TODO: extract from text
                experience = '1 Internship'  # TODO: extract from text """

                cgpa = extract_cgpa(text)
                skills = extract_skills(text)
                experience = extract_experience(text)

                status = 'shortlisted' if ai_score > 7 else 'review' 

                results.append({
                    'name': file.filename,
                    'score': round(ai_score, 2),
                    'cgpa': cgpa,
                    'skills': skills,
                    'experience': experience,
                    'status': status
                })


        results = sorted(results, key=lambda x: x['score'], reverse=True)

    return render_template('index.html', results=results)

if __name__ == '__main__':
    app.run(debug=True)
