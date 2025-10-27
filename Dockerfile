FROM python:3.13.9-slim

WORKDIR /cpu_simulator
COPY . /cpu_simulator

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "main.py"]

# example 
# docker run --rm cpu_simulator \
#  --instructions files/instruction_input.txt \
#  --memory files/data_input.txt
# 
