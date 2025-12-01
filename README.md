# Cloudflare Dynamic DNS

[![Build](https://github.com/LucAce/cloudflare-ddns/actions/workflows/publish-ghcr.yaml/badge.svg?branch=main)](https://github.com/LucAce/cloudflare-ddns/actions/workflows/publish-ghcr.yaml)
[![License: MIT](https://cdn.prod.website-files.com/5e0f1144930a8bc8aace526c/65dd9eb5aaca434fac4f1c34_License-MIT-blue.svg)](/LICENSE)

A Simple Python based application that updates a Cloudflare DNS A record entry with
a host's public IPv4 address.

The application polls Cloudflare's `cdn-cgi/trace` data every 15 minutes to
determine the host's public IPv4 address.  On start up and on a change of the
hosts IPv4 address, the application will update Cloudflare DNS A record for
the provided domain.

## Deploy with Docker Compose

Pre-built images are available via the GitHub Container Repository:
[ghcr.io/lucace/cloudflare-ddns](https://ghcr.io/lucace/cloudflare-ddns)

### Configuring the Docker Image

Copy and modify the `docker-compose.yml` file, setting the following environment variables:

| Variable           | Type    | Required | Default | Description                        |
|:------------------ |:------- |:--------:|:-------:|:---------------------------------- |
| CLOUDFLARE_API_KEY | String  | Yes      | _None_  | Cloudflare API Key                 |
| CLOUDFLARE_ZONE_ID | String  | Yes      | _None_  | Cloudflare DNS Entry Zone ID       |
| DOMAIN_NAME        | String  | Yes      | _None_  | Domain Name to Manage              |
| VERBOSE            | Boolean | No       | False   | Enable Verbose Messages            |
| DOMAIN_TTL         | Integer | No       | 3600    | DNS Record Time to Live in Seconds |
| UPDATE_RATE        | Integer | No       | 900     | Polling Update Rate in Seconds     |

> [!IMPORTANT]
> "{{ CLOUDFLARE_API_KEY }}", "{{ CLOUDFLARE_ZONE_ID }}", and "{{ DOMAIN NAME }}" in the
> `docker-compose.yml` file example are placeholders and must be replaced with actual values.

```yaml
services:
  cloudflare-ddns:
    container_name: cloudflare-ddns
    image: ghcr.io/lucace/cloudflare-ddns:latest
    environment:
      VERBOSE: True
      CLOUDFLARE_API_KEY: {{ CLOUDFLARE_API_KEY }}
      CLOUDFLARE_ZONE_ID: {{ CLOUDFLARE_ZONE_ID }}
      DOMAIN_NAME: {{ DOMAIN NAME }}
      DOMAIN_TTL: 3600
      UPDATE_RATE: 900
    restart: unless-stopped
    read_only: True
    cap_drop: [all]
    security_opt: [no-new-privileges:true]
```

### Running the Docker Image

From the directory containing docker-compose.yml, start the container:

```bash
docker compose up -d
```

## Cloudflare

This application requires a Cloudflare API Key and a Zone ID to update the DNS
entry for a domain.

### Cloudflare API Key

A Cloudflare API Key with DNS editing permissions is required.  The API key
should only include the specific zone (doman name) that will be updated.
Instructions on how to create an API Key can be found on Cloudflare's
developer documentation site:

https://developers.cloudflare.com/fundamentals/api/get-started/create-token/

### Cloudflare Zone ID

A Cloudflare Zone ID is a unique identifier Cloudflare assigns to each domain
(called a zone) in your Cloudflare account.  The Zone ID for the domain name
record that will be updated is required and can be found in the Cloudflare
web interface.  Instructions on how to determine what the Zone ID is for
a domain can be found on Cloudflare's developer documentation site:

https://developers.cloudflare.com/fundamentals/concepts/accounts-and-zones/ \
https://developers.cloudflare.com/fundamentals/account/find-account-and-zone-ids/
