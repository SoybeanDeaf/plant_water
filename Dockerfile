FROM python:3.8

COPY requirements.txt .
RUN pip install -r requirements.txt

ADD . /app
WORKDIR /app

CMD ["python", "/app/src/app.py"]