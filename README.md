# Cloudflare Dynamic DNS

Simple python based application that updates a Cloudflare DNS A record entry with
the host's public IPv4 address.

The application polls Cloudflare's `cdn-cgi/trace` data every 15 minutes to
determine the host's public IPv4 address.  On start up and on a change, the
new IPv4 address is updated.

# Deploy with Docker Compose

Pre-compiled images are available via the GitHub docker repository:
[ghcr.io/lucace/cloudflare-ddns](https://ghcr.io/lucace/cloudflare-ddns)

### Configuring the Docker Image

Copy and modify the `docker-compose.yml` file with the following environment variables:

| Variable           | Type        | Default |  Description                       |
|:------------------ |:----------- |:------- |:---------------------------------- |
| CLOUDFLARE_API_KEY | Required    | _None_  | Cloudflare API Key                 |
| CLOUDFLARE_ZONE_ID | Required    | _None_  | Cloudflare DNS Entry Zone ID       |
| DOMAIN_NAME        | Required    | _None_  | Domain Name to Manage              |
| VERBOSE            | Optional    | False   | Enable Verbose Messages            |
| DOMAIN_TTL         | Optional    | 3600    | DNS Record Time to Live in Seconds |
| UPDATE_RATE        | Optional    | 900     | Polling Update Rate in Seconds     |

[!NOTE]
"{{ CLOUDFLARE_API_KEY }}", "{{ CLOUDFLARE_ZONE_ID }}", "{{ DOMAIN NAME }}" in the
docker-compose.yml file are just placeholders and must be replaced with the actual values.

```yaml
services:
  cloudflare-ddns:
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

From the `docker-compose.yml` location, start the container.

```bash
docker-compose up -d
```
