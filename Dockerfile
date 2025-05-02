FROM python:3.12.9-alpine3.21

WORKDIR /app

RUN apk add --no-cache postgresql-dev

# Copy main requirements first
COPY ./requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy plugin requirements and install them
COPY ./plugins/*/requirements.txt /tmp/plugin_requirements/
RUN for req in /tmp/plugin_requirements/*requirements.txt; do \
    if [ -f "$req" ]; then \
    pip install --no-cache-dir -r "$req"; \
    fi \
    done

COPY . .

EXPOSE 8080

CMD ["gunicorn", "main:app", "-k", "uvicorn.workers.UvicornWorker", "-w", "4", "-b", "0.0.0.0:8080", "--log-config", "logging.conf"]
