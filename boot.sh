#!/bin/sh
source venv/bin/activate
exec gunicorn -b :5000 --workers 4 --access-logfile - --error-logfile - demos:app