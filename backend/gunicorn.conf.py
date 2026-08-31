"""Gunicorn configuration for production deployment."""

import multiprocessing
import os

bind = '0.0.0.0:8000'
workers = int(os.environ.get('GUNICORN_WORKERS', multiprocessing.cpu_count() * 2 + 1))
threads = int(os.environ.get('GUNICORN_THREADS', 2))
timeout = 120
graceful_timeout = 30
accesslog = '-'
errorlog = '-'
proc_name = 'leave_management'
