# Dockerfile
# Test framework container for Python Arena SDET suite.
#
# BUILD:  docker build -t python-arena .
# RUN:    docker run --rm python-arena
# TESTS:  docker run --rm python-arena pytest week1/ -v
#
# WHY EACH LINE EXISTS — read these comments.
# Docker best practice: document every decision.

# =============================================
# BASE IMAGE
# =============================================
# python:3.12-slim = Python 3.12 on Debian slim
# slim = stripped down Debian, no dev tools
# Why not python:3.12? Full image is 1GB+, slim is 200MB
# Why not alpine? Playwright does not support Alpine
# Why 3.12 specifically? Matches our CI and local setup
FROM python:3.12-slim

# =============================================
# SYSTEM DEPENDENCIES
# =============================================
# These are OS-level packages Playwright needs
# to run Chromium in headless mode.
# Without these, playwright install fails silently
# and browser tests crash with cryptic errors.
#
# --no-install-recommends = skip optional packages
# saves ~200MB
# rm -rf /var/lib/apt/lists/* = delete apt cache
# after installing — keeps image size small
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    curl \
    git \
    --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# =============================================
# WORKING DIRECTORY
# =============================================
# All subsequent commands run from /app
# Your code will live at /app inside the container
WORKDIR /app

# =============================================
# INSTALL PYTHON DEPENDENCIES
# =============================================
# Copy requirements BEFORE copying source code.
# WHY THIS ORDER MATTERS (Docker layer caching):
# Docker builds in layers. Each instruction = one layer.
# If requirements.txt has not changed, Docker reuses
# the cached pip install layer.
# If you copy all code first, any code change
# invalidates the cache and pip reinstalls everything.
# Copy requirements first = pip only reruns when
# requirements actually change. Builds go from
# 2 minutes to 15 seconds on code-only changes.
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# =============================================
# INSTALL PLAYWRIGHT BROWSERS
# =============================================
# Installs Chromium + all system dependencies
# --with-deps = installs OS packages Chromium needs
# This is the slowest step (~2 minutes)
# But it is cached after the first build
RUN playwright install --with-deps chromium

# =============================================
# COPY SOURCE CODE
# =============================================
# Copy everything AFTER pip install (cache reasons above)
# .dockerignore prevents copying .venv, __pycache__,
# .env, reports/ — keeps the image clean and small
COPY . .

# =============================================
# ENVIRONMENT VARIABLES
# =============================================
# PYTHONUNBUFFERED=1 means Python prints immediately
# Without this, print() output disappears in CI logs
# because Python buffers stdout
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# =============================================
# DEFAULT COMMAND
# =============================================
# What runs when you do: docker run python-arena
# Can be overridden: docker run python-arena pytest week5/ -v
CMD ["pytest", "week1/saturday_project/", "-v", "--tb=short"]