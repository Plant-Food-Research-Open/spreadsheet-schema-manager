# Use the official Python image as a base. This ensures that typical Python
# dependencies are already installed in the container.
FROM python:3.14-alpine

# Make port 8000 available to the outside world. This is the port Rio will run
# at
EXPOSE 8000

# Set environment variables to prevent Python from writing `.pyc` files and
# creating a buffer for stdout
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Set up CA certificates
COPY k8s-prod-ca.crt /usr/local/share/ca-certificates

COPY k8s-dev-ca.crt /usr/local/share/ca-certificates

COPY pfr-ca.crt /usr/local/share/ca-certificates

RUN apk add --no-cache ca-certificates \
 && update-ca-certificates

ENV REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt

# Set the working directory in the container
WORKDIR /app

# Install the latest version of `uv`. `uv` is similar to `pip`, but much faster
# and supports additional commands we'll use below
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Docker caches the results of each RUN instruction. Whenever a container is
# rebuilt, Docker will avoid running any steps whose results are still valid
# from last time.
#
# To make sure the dependencies don't all have to be reinstalled every time you
# change a single line of code, we'll install them before adding the bulk of the
# project files.
#
# Some build tools, like `poetry` require the project's README file to be
# present for this step. If your file is named differently or you don't have one
# at all, update this line or add a file.
# COPY pyproject.toml README.md /app/
# RUN uv pip install -r pyproject.toml --system --pre

# Alternatively, if you're using a `requirements.txt` file instead of
# `pyproject.toml`, you can use the following commands instead:
#
COPY requirements.txt /app
RUN uv pip install --system -r requirements.txt --pre

# Now copy the remainder of the project. This way if anything in the project
# changes the dependencies don't have to be reinstalled.
COPY . /app

# This command will be run by docker once you run the container. It starts the
# Rio server in release mode, on port 8000. We also make the port publicly
# available, so that Docker can expose it to the outside world.
CMD ["python", "-m", "rio", "run", "--release", "--port=8000", "--public"]