# Use official Python image as base
FROM python:3.11-slim

# Set working directory inside container
WORKDIR /app

# Copy requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your app files
COPY app.py .
COPY templates ./templates
COPY uploads ./uploads

# Expose the port your Flask app runs on (use 8000 if you plan to run with gunicorn)
EXPOSE 8000

# Run the app with gunicorn (recommended for production)
CMD ["gunicorn", "-b", "0.0.0.0:8000", "app:app"]
