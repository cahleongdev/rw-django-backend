FROM public.ecr.aws/docker/library/python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
  build-essential \
  libpq-dev \
  curl \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

RUN pip freeze > requirements.tsx
COPY requirements.txt /app/
RUN pip install --upgrade pip \
  && pip install --no-cache-dir -r requirements.txt

COPY . /app/

RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser
RUN chown -R appuser:appgroup /app
USER appuser

EXPOSE 8000

CMD ["uvicorn", "config.asgi:application", "--host", "0.0.0.0", "--port", "8000"]
