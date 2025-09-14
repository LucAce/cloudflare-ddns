# Use Alpine Linux Base Image
FROM alpine:latest

# Create and make the app directory the working path
WORKDIR /app

# Copy the script into the app directory
COPY src/cloudflare-ddns.py /app

# Get system updates and install dependencies
RUN apk update  && \
    apk upgrade && \
    apk add --no-cache python3 py3-requests

# Disable Python console buffering
ENV PYTHONUNBUFFERED=1

# Add the Build Date as an environment variable
ARG BUILD_DATE
ENV BUILD_DATE=$BUILD_DATE

# Dockerfile Labels
LABEL org.opencontainers.image.source="https://github.com/lucace/cloudflare-ddns"
LABEL org.opencontainers.image.description="Updates a Cloudflare DNS A Record with the hosts public IPv4 address"
LABEL org.opencontainers.image.licenses="MIT"

# Execute the script
CMD ["/usr/bin/python3", "/app/cloudflare-ddns.py"]
