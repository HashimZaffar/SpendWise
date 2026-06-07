FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

EXPOSE 5001

CMD ["sh", "-c", "python -c 'from app import initialize_database; initialize_database()' && gunicorn --bind 0.0.0.0:5001 app:app"]
