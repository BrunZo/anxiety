FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY py/ ./py/
COPY html/ ./html/
COPY content/ ./content/

RUN mkdir -p /data

EXPOSE 8000

ENV PYTHONUNBUFFERED=1
ENV PORT=8000

CMD ["python", "py/server.py"]

