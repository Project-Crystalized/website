# Gemini Server Deployment

Setup instructions for running the Gemini capsule with [Agate](https://github.com/mbrubeck/agate) on Debian.

## Prerequisites

- Agate installed (`/usr/local/bin/agate`)
- Repository cloned on the server

## Setup

```bash
# Symlink service file
sudo ln -s /var/www/html/gemini/gemini/deploy/agate.service /etc/systemd/system/agate.service

# Create certs directory (agate generates TLS certs here on first run)
sudo mkdir -p /var/lib/agate/certs
sudo chown www-data:www-data /var/lib/agate/certs

# Enable and start
sudo systemctl daemon-reload
sudo systemctl enable --now agate
```

## Updating

After pulling new changes:

```bash
sudo systemctl daemon-reload
sudo systemctl restart agate
```

## Removing

```bash
sudo systemctl disable --now agate
sudo rm /etc/systemd/system/agate.service
sudo systemctl daemon-reload
```
