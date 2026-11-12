#!/bin/bash
# ==============================================================================
# AWS EC2 Provisioning Script (Ubuntu 22.04 / 24.04 LTS)
# Target Region: ap-southeast-2 (Sydney)
# ==============================================================================
set -e

echo "=== 1. Updating System Packages ==="
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3-pip python3-venv git nginx certbot python3-certbot-nginx libmysqlclient-dev

echo "=== 2. Setting Up Project Directory ==="
sudo mkdir -p /var/www/helpdesk
sudo chown -R ubuntu:ubuntu /var/www/helpdesk

# Assuming repo is cloned to /var/www/helpdesk
cd /var/www/helpdesk

echo "=== 3. Python Virtual Environment & Backend Setup ==="
cd /var/www/helpdesk/backend
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Create upload directory and set permissions
mkdir -p app/uploads
sudo chown -R ubuntu:www-data app/uploads
sudo chmod -R 770 app/uploads

echo "=== 4. Building React Production Bundle ==="
# Install Node.js 20 LTS if not present
if ! command -v node &> /dev/null; then
    curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
    sudo apt install -y nodejs
fi

cd /var/www/helpdesk/frontend
npm ci
npm run build

echo "=== 5. Configuring Systemd Gunicorn Service ==="
sudo mkdir -p /var/log/helpdesk
sudo chown -R ubuntu:ubuntu /var/log/helpdesk
sudo cp /var/www/helpdesk/deployment/helpdesk.service /etc/systemd/system/helpdesk.service
sudo systemctl daemon-reload
sudo systemctl enable helpdesk
sudo systemctl restart helpdesk

echo "=== 6. Configuring Nginx ==="
sudo cp /var/www/helpdesk/deployment/nginx.conf /etc/nginx/sites-available/helpdesk
sudo ln -sf /etc/nginx/sites-available/helpdesk /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx

echo "=== Deployment Setup Complete ==="
echo "Run 'sudo certbot --nginx -d yourdomain.com' to provision free HTTPS certificate."
