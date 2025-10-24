# Use a lightweight Python image that allows apt installs
FROM python:3.11-slim

# Install system dependencies for Tesseract and OpenCV
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libtesseract-dev \
    libgl1 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy backend files
COPY backend ./backend

# Set backend as working directory (where main.py lives)
WORKDIR /app/backend

# Install uv and project dependencies (from pyproject.toml or requirements.txt)
RUN pip install uv && \
    if [ -f pyproject.toml ]; then \
        uv pip install .; \
    elif [ -f requirements.txt ]; then \
        pip install -r requirements.txt; \
    fi

# Expose port 8000
EXPOSE 8000

# Run FastAPI app via uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
