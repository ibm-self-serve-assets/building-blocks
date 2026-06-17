FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py main.py
COPY app/ app/

EXPOSE 8080

CMD ["python", "main.py"]
