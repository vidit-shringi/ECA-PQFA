FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
# Shared/container deployments require an explicit API key. Set
# ECA_PQFA_API_KEY through the runtime secret manager, never bake it into the image.
ENV ECA_PQFA_REQUIRE_API_KEY=true
CMD ["uvicorn","backend.app.main:app","--host","0.0.0.0","--port","8000"]
