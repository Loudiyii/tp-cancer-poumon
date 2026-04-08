FROM python:3.11-slim

WORKDIR /app

# Install system deps for TensorFlow / PIL
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Install Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir \
        fastapi==0.115.6 \
        "uvicorn[standard]==0.34.0" \
        python-multipart==0.0.20 \
        numpy==2.1.3 \
        pandas==2.2.3 \
        scikit-learn==1.6.1 \
        joblib==1.4.2 \
        Pillow==11.1.0 \
        matplotlib==3.10.8 \
        seaborn==0.13.2 \
        tensorflow==2.18.0

# Copy code and data
COPY backend ./backend
COPY src ./src
COPY data ./data
COPY model ./model

# Port for Render
ENV PORT=8000
ENV MODEL_DIR=/app/model
EXPOSE 8000

# Start FastAPI
CMD ["sh", "-c", "uvicorn backend.main:app --host 0.0.0.0 --port ${PORT}"]
