FROM python:3.11-slim-buster
LABEL authors="BlankAtomic"

WORKDIR /app

COPY . /app

EXPOSE 5000

RUN pip install --upgrade pip
RUN pip install opencv-python-headless
RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "api.py"]