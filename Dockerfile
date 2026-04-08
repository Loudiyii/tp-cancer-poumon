FROM python:3.11-slim

WORKDIR /app

# System deps for TensorFlow / PIL
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Python deps (tensorflow-cpu is lighter than tensorflow for free tier)
COPY backend/requirements.txt /app/backend/requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r /app/backend/requirements.txt

# Copy code and models
COPY backend ./backend
COPY model ./model

# Port for Render
ENV PORT=8000
ENV MODEL_DIR=/app/model
ENV PYTHONUNBUFFERED=1
EXPOSE 8000

# Start FastAPI
CMD ["sh", "-c", "uvicorn backend.main:app --host 0.0.0.0 --port ${PORT}"]
