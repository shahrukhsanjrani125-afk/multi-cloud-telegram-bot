#!/bin/bash

echo "🦈 Setting up Shark ERP System..."

# Install dependencies
echo "Installing Python dependencies..."
pip3 install -r requirements.txt

# Setup directories
echo "Creating directory structure..."
mkdir -p logs data config google_sheets

# Setup Tor
echo "Configuring Tor..."
sudo apt-get update
sudo apt-get install -y tor

# Create Tor configuration
sudo tee /etc/tor/torrc.shark << EOF
SocksPort 9050
ControlPort 9051
HashedControlPassword 16:872860B76453A77D60CA2BB8C1A7042072093276A3D701AD684053EC4C
Log notice file /var/log/tor/notices.log
DataDirectory /var/lib/tor
EOF

# Setup systemd service
echo "Creating systemd service..."
sudo tee /etc/systemd/system/shark-erp.service << EOF
[Unit]
Description=Shark ERP System
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$(pwd)
ExecStart=$(pwd)/run_shark.sh
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOF

# Setup environment file
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    tee .env << EOF
# Telegram Configuration
TELEGRAM_TOKEN=your_bot_token_here
ADMIN_CHAT_ID=your_chat_id_here

# OpenStack Configuration
OPENSTACK_URL=http://127.0.0.1:8080
OPENSTACK_USERNAME=admin
OPENSTACK_PASSWORD=password123

# Google Sheets
SPREADSHEET_ID=your_sheet_id_here

# App Configuration
DEBUG=False
LOG_LEVEL=INFO
EOF
    echo "Please edit .env file with your credentials"
fi

# Make scripts executable
chmod +x run_shark.sh
chmod +x setup.sh

echo ""
echo "✅ Setup complete!"
echo "Next steps:"
echo "1. Edit .env file with your credentials"
echo "2. Place Google Sheets credentials in google_sheets/credentials.json"
echo "3. Run: ./run_shark.sh"
echo "4. Or run with systemd: sudo systemctl start shark-erp"