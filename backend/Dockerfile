# ./code-runner/Dockerfile
FROM python:3.12-slim

# Create a non-root user for security
RUN useradd -m runner
USER runner

# Work inside this directory
WORKDIR /app

# Accept code and input as files
COPY codeRunner.py .

CMD ["python", "codeRunner.py"]
