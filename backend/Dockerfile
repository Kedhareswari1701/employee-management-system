# Backend Dockerfile - Django + Gunicorn
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Render ignores EXPOSE and instead injects the listen port via $PORT,
# which gunicorn.conf.py reads at runtime.
EXPOSE 8000

# Collect static files and run migrations before starting the server
CMD ["sh", "-c", "python manage.py migrate --noinput && \
    python manage.py collectstatic --noinput && \
    gunicorn core.wsgi:application --config gunicorn.conf.py"]
