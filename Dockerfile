# Official Python Image
FROM python:3.9-slim

# Working directory
WORKDIR /app

# Copies application code to the container
COPY . /app

# Links the code to the image in GitHub
LABEL org.opencontainers.image.source https://github.com/ewsmyth/owow

# Install the dependencies from requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Exposes port
EXPOSE 6876

# Command to run server
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:6876", "owow:app"]