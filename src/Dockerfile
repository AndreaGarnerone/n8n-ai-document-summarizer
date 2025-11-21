FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias del sistema para PDF processing
RUN apt-get update && apt-get install -y \
    poppler-utils \
    tesseract-ocr \
    tesseract-ocr-spa \
    libreoffice \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements
COPY requirements.txt .

# Instalar dependencias Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código
COPY . .

# Puerto para API
EXPOSE 8000

# Comando por defecto
CMD ["python", "api_server.py"]