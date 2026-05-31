FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy and install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend files
COPY . .

EXPOSE 8080

# Set production env flags
ENV PORT=8080
ENV DATABASE_PATH=/app/data/faithguide.db
ENV CHROMA_PATH=/app/data/chromadb

# Use production server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
