FROM python:3.10-slim

WORKDIR /app

# System deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Expose ports: 7860 (FastAPI env), 8501 (Streamlit UI)
EXPOSE 7860 8501

# Start both services via shell script
CMD ["bash", "start.sh"]
