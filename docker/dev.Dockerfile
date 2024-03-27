FROM python:3.10.6-slim

WORKDIR /astrikos-worker/
COPY ./requirements.txt /astrikos-worker
RUN pip install -r requirements.txt

COPY . .

ENV FLASK_APP=app.py
CMD ["flask", "run", "--host", "0.0.0.0"]