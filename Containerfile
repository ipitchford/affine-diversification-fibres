FROM python:3.13.5-slim@sha256:4c2cf9917bd1cbacc5e9b07320025bdb7cdf2df7b0ceaccb55e9dd7e30987419

WORKDIR /work
COPY requirements-lock.txt ./
RUN python -m pip install --no-cache-dir -r requirements-lock.txt
COPY . .
ENV PYTHONPATH=/work
CMD ["python", "verification/replay_release.py"]
