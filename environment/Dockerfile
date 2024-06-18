FROM python:3.10.6-slim

WORKDIR /app

RUN pip install requests

COPY . .

RUN echo ${download_script} > ./download_script.py

RUN python download_script.py ${download_url}

RUN pip install -r ./requirements.txt
RUN pip install -r ./requirements_flow.txt
