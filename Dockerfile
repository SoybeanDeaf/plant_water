FROM python:3.8
WORKDIR /app

COPY setup.py .
COPY src/ .

RUN pip install .

CMD ["python", "./plant_water/app.py"]