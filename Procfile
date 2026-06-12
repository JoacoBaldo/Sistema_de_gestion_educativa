web: gunicorn --bind 0.0.0.0:${PORT:-5000} --workers 1 --worker-class sync --timeout 120 --access-logfile - --error-logfile - --log-level debug app:app
