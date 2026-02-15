#!/bin/bash
set -euo pipefail

DOMAIN=${1:-dashovia.com}
API_DOMAIN=${2:-api.dashovia.com}

export DEBIAN_FRONTEND=noninteractive

apt-get update -y
apt-get install -y debian-keyring debian-archive-keyring apt-transport-https curl
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | tee /etc/apt/sources.list.d/caddy-stable.list
apt-get update -y
apt-get install -y caddy

cat > /etc/caddy/Caddyfile <<EOF
$DOMAIN {
  reverse_proxy localhost:3000
}

$API_DOMAIN {
  reverse_proxy localhost:8000
}
EOF

systemctl enable --now caddy
systemctl reload caddy

APP_DIR=/opt/udaan
cd "$APP_DIR"

cat > deploy/aws/.env.prod <<EOF
PUBLIC_BASE_URL=https://$API_DOMAIN
NEXT_PUBLIC_API_URL=https://$API_DOMAIN
EOF

sed -i.bak "s|^PUBLIC_BASE_URL=.*|PUBLIC_BASE_URL=https://$API_DOMAIN|" backend/.env

docker compose -f deploy/aws/docker-compose.prod.yml --env-file deploy/aws/.env.prod up -d --build

echo "HTTPS configured for $DOMAIN and $API_DOMAIN"
