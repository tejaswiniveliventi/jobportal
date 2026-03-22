FROM python:3.11-slim

# System deps needed by: psycopg2, pdfminer, pymupdf, spacy, chromadb
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    libffi-dev \
    libssl-dev \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python deps first (cached layer)
COPY requirements.txt .

# Upgrade pip first — old pip misresolves many packages
RUN pip install --upgrade pip setuptools wheel

# Install in two passes: heavy AI/ML stack first, then app deps
# This gives clearer error messages if something fails
RUN pip install --no-cache-dir \
    spacy==3.7.4 \
    chromadb==0.5.0 \
    google-generativeai==0.5.4

RUN pip install --no-cache-dir \
    langgraph==0.1.19 \
    langchain-core==0.2.9

RUN pip install --no-cache-dir -r requirements.txt

# Download spaCy model
RUN python -m spacy download en_core_web_sm

COPY . .

RUN mkdir -p /app/uploads /app/chromadb_data

EXPOSE 8000
