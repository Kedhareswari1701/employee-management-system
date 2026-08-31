"""Gunicorn configuration for production deployment."""

import os

# Render (and other PaaS) inject the port to listen on via $PORT.
# Fall back to 8000 for local docker-compose development.
port = os.environ.get('PORT', '8000')
bind = f'0.0.0.0:{port}'

# NEVER auto-scale workers from CPU count on a shared/512MiB container:
# each worker is a full Django process (~100-150MB), so cpu_count()*2+1
# can easily OOM the instance. Keep a small fixed default and allow an
# override via env var (Render: WEB_CONCURRENCY).
default_workers = 2
workers = int(
    os.environ.get(
        'WEB_CONCURRENCY',
        os.environ.get('GUNICORN_WORKERS', default_workers),
    )
)
threads = int(os.environ.get('GUNICORN_THREADS', 2))

# Load the app once in the master process and fork, sharing memory pages
# via copy-on-write. Significantly reduces per-worker memory usage.
preload_app = True

timeout = 120
graceful_timeout = 30
accesslog = '-'
errorlog = '-'
proc_name = 'leave_management'
