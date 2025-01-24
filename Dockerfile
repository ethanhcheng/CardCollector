FROM python:3.10-slim

WORKDIR /app

COPY webapp/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY webapp /app/

EXPOSE 8080

CMD [ "python3", "app.py" ]