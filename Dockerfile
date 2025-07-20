# Use Alpine Linux Base Image
FROM alpine:latest

# Create and make the app directory the working path
WORKDIR /app

# Copy the script into the app directory
COPY src/cloudflare-ddns.py /app

# Disable Python console buffering
ENV PYTHONUNBUFFERED=1

# Get system updates and install dependencies
RUN apk update  && \
    apk upgrade && \
    apk add --no-cache python3 py3-requests

# Execute the script in service mode
CMD ["/usr/bin/python3", "/app/cloudflare-ddns.py"]
