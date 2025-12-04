# Basimage
FROM python:3.11-slim

# Sätt arbetskatalog
WORKDIR /app

# Installera beroenden
COPY requirements/prod.txt /tmp/
RUN pip install --no-cache-dir -r /tmp/prod.txt

# Kopiera in app-koden
COPY app/ ./app

# Exponera port för Flask
EXPOSE 8000

# Miljövariabler direkt i container (kan även sättas via docker-compose.yml)
ENV PYTHONUNBUFFERED=1

# Starta Flask-appen
CMD ["flask", "run", "--host=0.0.0.0", "--port=8000"]
