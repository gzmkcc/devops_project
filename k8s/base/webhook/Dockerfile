FROM python:3.11-slim

WORKDIR /app

RUN pip install flask

COPY webhook.py .

EXPOSE 8443

CMD ["python", "webhook.py"]