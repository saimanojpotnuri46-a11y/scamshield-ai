FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY . .

EXPOSE 8501 8000

# Start both REST API (port 8000) and Streamlit Dashboard (port 8501)
CMD ["sh", "-c", "python -m uvicorn src.api:app --host 0.0.0.0 --port 8000 & python -m streamlit run src/app.py --server.port 8501 --server.address 0.0.0.0"]
