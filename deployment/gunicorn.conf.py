# Gunicorn Production Configuration
import multiprocessing

bind = "127.0.0.1:8000"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
timeout = 60
keepalive = 5
max_requests = 1000
max_requests_jitter = 50

# Logging
accesslog = "/var/log/helpdesk/gunicorn_access.log"
errorlog = "/var/log/helpdesk/gunicorn_error.log"
loglevel = "info"
capture_output = True
