#!/bin/bash

if [ "$EUID" -ne 0 ]; then
  echo -e "ERROR: Please run as root\n"
  exit
fi

# Stop cloudflare-ddns
docker stop cloudflare-ddns

# Remove cloudflare-ddns
docker image rm -f cloudflare-ddns-cloudflare-ddns

# Purge cache
docker system prune -f

# Build cloudflare-ddns
pushd ../src/ > /dev/null
docker compose -f docker-compose.yml up -d --build  --force-recreate
popd > /dev/null
