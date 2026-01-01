from telegram import Update
from telegram.ext import ContextTypes
import logging
from datetime import datetime

from bot.states import States
from bot.database import Database
from openstack.client import OpenStackClient
from google_sheets.sheets_api import GoogleSheetsAPI
from tor_proxy.socks5_proxy import make_tor_request

logger = logging.getLogger(__name__)
db = Database()
openstack_client = OpenStackClient()
sheets_api = GoogleSheetsAPI()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command handler"""
    await update.message.reply_text(
        "🦈 Welcome to Shark ERP System!\n\n"
        "Please enter the data you want to store in the ERP system.\n"
        "Format: Category|Description|Amount\n\n"
        "Example: Office Supplies|Printer Paper|1500"
    )
    return States.ENTERING_DATA

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle incoming messages"""
    user_data = update.message.text
    user_id = update.effective_user.id
    
    try:
        # Parse data
        parts = user_data.split('|')
        if len(parts) != 3:
            await update.message.reply_text(
                "❌ Invalid format. Please use: Category|Description|Amount"
            )
            return States.ENTERING_DATA
        
        category, description, amount = parts
        
        # Store in local database
        db.insert_entry({
            'user_id': user_id,
            'category': category,
            'description': description,
            'amount': float(amount),
            'timestamp': datetime.utcnow().isoformat()
        })
        
        # Upload to OpenStack via Tor
        success_openstack = await upload_to_openstack(category, description, amount, user_id)
        
        # Upload to Google Sheets
        success_sheets = upload_to_google_sheets(category, description, amount, user_id)
        
        # Send confirmation
        if success_openstack and success_sheets:
            await update.message.reply_text(
                "✅ Data successfully stored in both OpenStack and Google Sheets!"
            )
        else:
            await update.message.reply_text(
                "⚠️ Data stored with partial success. Check admin logs."
            )
        
        return States.ENTERING_DATA
        
    except Exception as e:
        logger.error(f"Error processing message: {e}")
        await update.message.reply_text("❌ Error processing your data. Please try again.")
        return States.ENTERING_DATA

async def upload_to_openstack(category, description, amount, user_id):
    """Upload data to OpenStack via Tor"""
    try:
        data = {
            'category': category,
            'description': description,
            'amount': amount,
            'user_id': user_id,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Make request through Tor
        response = make_tor_request(
            method='PUT',
            url=f"{openstack_client.base_url}/{category}/{user_id}_{datetime.now().timestamp()}",
            data=data
        )
        
        return response.status_code == 201
    except Exception as e:
        logger.error(f"OpenStack upload failed: {e}")
        return False

def upload_to_google_sheets(category, description, amount, user_id):
    """Upload data to Google Sheets"""
    try:
        sheets_api.append_row([
            datetime.utcnow().isoformat(),
            str(user_id),
            category,
            description,
            str(amount)
        ])
        return True
    except Exception as e:
        logger.error(f"Google Sheets upload failed: {e}")
        return False

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel operation"""
    await update.message.reply_text("Operation cancelled.")
    return ConversationHandler.END