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

# ---- Expose default port (for documentation only) ----
EXPOSE 10000

# ---- Start FastAPI using dynamic Render PORT ----
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-10000}"]
