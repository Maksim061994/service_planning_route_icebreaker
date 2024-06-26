import multiprocessing


# -b
bind = "0.0.0.0:8000"

# -w
workers = multiprocessing.cpu_count() * 1 + 2
worker_connections = 1000
threads = 1
max_requests = 3000

# -t
timeout = 600

# логирование
accesslog = '-'

# worker_class=uvicorn.workers.UvicornWorker
debug = True
logfile = '/var/log/gunicorn/debug.log'
loglevel = 'debug'
