# ---- Base Image ----
FROM python:3.11-slim

# ---- Install System Dependencies ----
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libtesseract-dev \
    libgl1 \
    && rm -rf /var/lib/apt/lists/*

# ---- Set Workdir ----
WORKDIR /app

# ---- Copy Backend ----
COPY backend ./backend

# ---- Switch to Backend Folder ----
WORKDIR /app/backend

# ---- Install Python Dependencies ----
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ---- Expose App Port ----
EXPOSE 8000

# ---- Start FastAPI ----
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
