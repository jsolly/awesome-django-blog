"""Gunicorn *production* config file"""

import multiprocessing
workers = multiprocessing.cpu_count() * 2 + 1
