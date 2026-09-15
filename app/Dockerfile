FROM python:3.12-slim

WORKDIR /app

COPY app/requirements.txt ./app/requirements.txt
RUN pip install --no-cache-dir -r app/requirements.txt

COPY alembic.ini ./
COPY alembic ./alembic
COPY app/ ./app/

RUN adduser --disabled-password --gecos "" appuser

RUN chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

CMD ["sh", "-c", "alembic upgrade head && exec uvicorn app.src.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
