FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY emitter.py emitter.py

ENTRYPOINT ["python", "emitter.py"]
