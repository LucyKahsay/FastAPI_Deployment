# BUILD STAGE
FROM python:3.14.4-slim-bookworm AS builder
# FROM tells Docker to start a new build 
# stage using the specified base image
# AS builder gives that stage the name builder.



WORKDIR /app

RUN python -m venv /opt/venv

COPY requirements.txt ./
RUN /opt/venv/bin/pip install --no-cache-dir -r requirements.txt


# Copy app code and install project
COPY . ./



# PRODUCTION STAGE
FROM python:3.14.4-slim-bookworm

WORKDIR /app

# Run as non-root user for security
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

COPY --from=builder --chown=appuser:appuser /opt/venv /opt/venv


# Copy app and dependencies from builder stage
COPY --from=builder --chown=appuser:appuser /app /app

ENV PATH="/opt/venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1
ENV PORT=8080





# exec replaces shell so fastapi receives SIGTERM for clean shutdown
CMD ["/bin/sh", "-c", "exec uvicorn main:app --host 0.0.0.0 --port \"$PORT\" --proxy-headers --forwarded-allow-ips '*'"]

