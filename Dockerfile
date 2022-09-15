FROM python:3.8-slim-buster

COPY . /app/

RUN apt update && apt install -y software-properties-common
RUN pip3 install --upgrade pip

WORKDIR /app/

RUN pip install --no-cache-dir -r requirements.txt

ENTRYPOINT ["python", "main.py"]