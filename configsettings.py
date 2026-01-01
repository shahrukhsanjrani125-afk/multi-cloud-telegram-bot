import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Telegram
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
    ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")
    
    # OpenStack
    OPENSTACK_URL = os.getenv("OPENSTACK_URL", "http://127.0.0.1:8080")
    OPENSTACK_AUTH_URL = os.getenv("OPENSTACK_AUTH_URL")
    OPENSTACK_USERNAME = os.getenv("OPENSTACK_USERNAME")
    OPENSTACK_PASSWORD = os.getenv("OPENSTACK_PASSWORD")
    OPENSTACK_TENANT_NAME = os.getenv("OPENSTACK_TENANT_NAME")
    
    # Tor Configuration
    TOR_SOCKS_PORT = 9050
    TOR_CONTROL_PORT = 9051
    TOR_PASSWORD = os.getenv("TOR_PASSWORD", "shark_erp_password")
    
    # Google Sheets
    GOOGLE_SHEETS_CREDENTIALS = "google_sheets/credentials.json"
    SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")
    
    # App Configuration
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")