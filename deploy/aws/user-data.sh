#!/bin/bash
set -euo pipefail

export DEBIAN_FRONTEND=noninteractive

apt-get update -y
apt-get install -y docker.io docker-compose-plugin git curl
systemctl enable --now docker

PUBLIC_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4 || true)
if [ -z "$PUBLIC_IP" ]; then
  PUBLIC_IP="localhost"
fi

APP_DIR=/opt/udaan
if [ ! -d "$APP_DIR" ]; then
  git clone https://github.com/Meet2147/Udaan.git "$APP_DIR"
fi

cd "$APP_DIR"

SECRET_KEY=$(openssl rand -hex 32)
VIDEO_SIGNING_SECRET=$(openssl rand -hex 32)

cat > backend/.env <<EOF
APP_NAME=Udaan API
ENV=production
SECRET_KEY=$SECRET_KEY
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
VIDEO_SIGNING_SECRET=$VIDEO_SIGNING_SECRET
DATABASE_URL=postgresql+psycopg2://postgres:postgres@db:5432/udaan
LOCAL_STORAGE_PATH=/app/storage
PUBLIC_BASE_URL=http://$PUBLIC_IP:8000
ADMIN_EMAIL=
ADMIN_PASSWORD=
ADMIN_FULL_NAME=
ADMIN_PHONE=
ADMIN_GRADE=
SUPERADMIN_EMAIL=meet@dashovia.com
SUPERADMIN_PASSWORD=Mahantam#6559
SUPERADMIN_FULL_NAME=Meet Jethwa
SUPERADMIN_PHONE=8928304380
SUPERADMIN_GRADE=NA
SONAR_API_KEY=
OPENAI_API_KEY=
RAZORPAY_KEY_ID=
RAZORPAY_KEY_SECRET=
RAZORPAY_WEBHOOK_SECRET=
ADMIN_SUBSCRIPTION_PRICE_INR=11000
SUPERADMIN_COMMISSION_PCT=10
EOF

cat > deploy/aws/.env.prod <<EOF
PUBLIC_BASE_URL=http://$PUBLIC_IP:8000
NEXT_PUBLIC_API_URL=http://$PUBLIC_IP:8000
EOF

docker compose -f deploy/aws/docker-compose.prod.yml --env-file deploy/aws/.env.prod up -d --build
