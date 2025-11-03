FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y build-essential libpq-dev curl && rm -rf /var/lib/apt/lists/*

COPY web/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY web/ .

COPY flag.txt /flag.txt

RUN mkdir -p /app/logs

EXPOSE 3000

CMD ["bash", "-c", "python init_admin.py && flask run --host=0.0.0.0 --port=3000"]