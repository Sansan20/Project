FROM python:3.10-slim

WORKDIR /app

COPY app/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY app/ ./app/

EXPOSE 8080

CMD ["python", "app/app.py"]
