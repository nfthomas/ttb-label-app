# Use a lightweight Python base with apt support
FROM python:3.11-slim

# Install Tesseract + OpenCV deps
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libtesseract-dev \
    libgl1 \
    && rm -rf /var/lib/apt/lists/*

# Set workdir
WORKDIR /app

# Copy backend code
COPY backend ./backend

# Switch to backend where pyproject.toml and main.py live
WORKDIR /app/backend

# Install dependencies (system-wide)
RUN pip install --no-cache-dir uv && \
    if [ -f pyproject.toml ]; then \
        uv pip install --system .; \
    elif [ -f requirements.txt ]; then \
        pip install --no-cache-dir -r requirements.txt; \
    fi

# Expose app port
EXPOSE 8000

# Run FastAPI app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
