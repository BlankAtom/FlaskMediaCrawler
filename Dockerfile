FROM mcr.microsoft.com/playwright/python:v1.42.0-jammy
LABEL authors="BlankAtomic"

WORKDIR /app

COPY . /app

EXPOSE 5000

RUN pip install --upgrade pip
RUN pip install opencv-python-headless
RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "api.py"]