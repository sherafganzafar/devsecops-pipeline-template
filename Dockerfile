FROM python:3.12-slim

WORKDIR /srv
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
RUN useradd --no-create-home appuser
USER appuser

EXPOSE 8000
# gthread: several workers and threads, so one idle connection (e.g. a load balancer
# health probe) cannot block /health. The default "sync" worker handles one at a time.
CMD ["gunicorn", "--worker-class", "gthread", "--workers", "2", "--threads", "4", "--timeout", "30", "-b", "0.0.0.0:8000", "app.main:app"]
