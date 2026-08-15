FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY requirements.txt pyproject.toml setup.py ./
COPY src ./src
RUN for attempt in 1 2 3; do \
      pip install --no-cache-dir --retries 10 --timeout 120 -r requirements.txt && pip check && exit 0; \
      echo "Dependency installation attempt ${attempt} failed; retrying..."; \
      sleep $((attempt * 10)); \
    done; \
    exit 1

COPY . ./

EXPOSE 8080

CMD ["python", "app.py"]
