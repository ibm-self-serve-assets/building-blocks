FROM python:3.11

# Set the working directory inside the container
WORKDIR /app/backend

# Copy the requirements file to the container and install dependencies
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

# Copy your FastAPI Python script to the container
COPY main.py main.py
COPY app/ app/

EXPOSE 4050

# Set the command to run your Python script
CMD ["python3", "main.py"]
