#!/bin/bash
set -euo pipefail

DOMAIN=${1:-dashovia.com}
API_DOMAIN=${2:-api.dashovia.com}

export DEBIAN_FRONTEND=noninteractive

if command -v apt-get >/dev/null 2>&1; then
  apt-get update -y
  apt-get install -y debian-keyring debian-archive-keyring apt-transport-https curl
  curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
  curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | tee /etc/apt/sources.list.d/caddy-stable.list
  apt-get update -y
  apt-get install -y caddy
elif command -v dnf >/dev/null 2>&1; then
  dnf install -y curl ca-certificates
  if dnf install -y 'dnf-command(copr)' && dnf copr enable -y @caddy/caddy && dnf install -y caddy; then
    :
  else
    echo "Copr repo unavailable; installing Caddy binary."
    ARCH=$(uname -m)
    if [ "$ARCH" = "x86_64" ]; then
      ARCH="amd64"
    elif [ "$ARCH" = "aarch64" ]; then
      ARCH="arm64"
    fi
    CADDY_VERSION="2.8.4"
    curl -L "https://github.com/caddyserver/caddy/releases/download/v${CADDY_VERSION}/caddy_${CADDY_VERSION}_linux_${ARCH}.tar.gz" -o /tmp/caddy.tgz
    tar -xzf /tmp/caddy.tgz -C /tmp
    install -m 0755 /tmp/caddy /usr/local/bin/caddy
  fi
else
  echo "Unsupported OS: no apt-get or dnf found"
  exit 1
fi

mkdir -p /etc/caddy
cat > /etc/caddy/Caddyfile <<EOF
$DOMAIN {
  reverse_proxy localhost:3000
}

$API_DOMAIN {
  reverse_proxy localhost:8000
}
EOF

if [ -f /etc/systemd/system/caddy.service ] || systemctl list-unit-files | grep -q caddy.service; then
  systemctl enable --now caddy
  systemctl reload caddy
else
  cat > /etc/systemd/system/caddy.service <<EOF
[Unit]
Description=Caddy
After=network.target

[Service]
ExecStart=/usr/local/bin/caddy run --config /etc/caddy/Caddyfile --adapter caddyfile
ExecReload=/usr/local/bin/caddy reload --config /etc/caddy/Caddyfile --adapter caddyfile
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOF
  systemctl daemon-reload
  systemctl enable --now caddy
fi

APP_DIR=/opt/udaan
cd "$APP_DIR"

cat > deploy/aws/.env.prod <<EOF
PUBLIC_BASE_URL=https://$API_DOMAIN
NEXT_PUBLIC_API_URL=https://$API_DOMAIN
EOF

sed -i.bak "s|^PUBLIC_BASE_URL=.*|PUBLIC_BASE_URL=https://$API_DOMAIN|" backend/.env

if command -v docker-compose >/dev/null 2>&1; then
  docker-compose -f deploy/aws/docker-compose.prod.yml --env-file deploy/aws/.env.prod up -d --build
else
  docker compose -f deploy/aws/docker-compose.prod.yml --env-file deploy/aws/.env.prod up -d --build
fi

echo "HTTPS configured for $DOMAIN and $API_DOMAIN"
