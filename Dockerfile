FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY requirements.txt pyproject.toml setup.py ./
COPY src ./src
RUN pip install --no-cache-dir -r requirements.txt

COPY . ./

EXPOSE 8080

CMD ["python", "app.py"]
