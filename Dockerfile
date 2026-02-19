FROM python:3.12-slim

WORKDIR /cpu_simulator
COPY . /cpu_simulator

RUN pip install --no-cache-dir -r requirements.txt

ENTRYPOINT ["python"]
CMD ["main.py", "--instructions", "files/instruction_input.txt", "--memory", "files/data_input.txt"]
