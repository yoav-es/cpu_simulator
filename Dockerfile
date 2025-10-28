FROM python:3.13.9-slim

WORKDIR /cpu_simulator
COPY . /cpu_simulator

RUN pip install --no-cache-dir -r requirements.txt

ENTRYPOINT ["python", "main.py"]
