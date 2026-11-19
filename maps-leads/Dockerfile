# لأي استضافة بتشغّل Docker (Railway, Fly.io, VPS...). على Render استخدم render.yaml.
FROM python:3.12-slim
WORKDIR /app
COPY . .
ENV HOST=0.0.0.0 PORT=8080 DATA_DIR=/data PYTHONUNBUFFERED=1
VOLUME ["/data"]
EXPOSE 8080
CMD ["python", "app.py", "--no-browser"]
