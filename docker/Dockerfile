# Basimage
FROM python:3.11-slim

# Sätt arbetskatalog
WORKDIR /app

# Installera system dependencies för MySQL FÖRST
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Installera Python dependencies
COPY requirements/prod.txt /tmp/
RUN pip install --upgrade setuptools
RUN pip install --no-cache-dir -r /tmp/prod.txt

RUN pip uninstall -y setuptools
# Kopiera HELA applikationen (app/, microblog.py, migrations/, etc)
COPY . .

# Miljövariabler
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=microblog.py

# Exponera port
EXPOSE 8000

# Kör migrations OCH starta Flask
CMD flask db upgrade && flask run --host=0.0.0.0 --port=8000