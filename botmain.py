import logging
from telegram import Update
from telegram.ext import (
    Application, CommandHandler, MessageHandler, 
    filters, ContextTypes, ConversationHandler
)
import asyncio
from datetime import datetime

from config.settings import Config
from bot.handlers import start, handle_message, cancel
from bot.states import States
from bot.database import Database
from tor_proxy.tor_manager import TorManager

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=getattr(logging, Config.LOG_LEVEL)
)
logger = logging.getLogger(__name__)

class ERPBot:
    def __init__(self):
        self.config = Config
        self.db = Database()
        self.tor_manager = TorManager()
        
    async def start_bot(self):
        """Start the Telegram bot"""
        # Start Tor proxy
        if not self.tor_manager.start_tor():
            logger.error("Failed to start Tor proxy")
            return
        
        # Create application
        application = Application.builder().token(self.config.TELEGRAM_TOKEN).build()
        
        # Conversation handler
        conv_handler = ConversationHandler(
            entry_points=[CommandHandler('start', start)],
            states={
                States.ENTERING_DATA: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
                ],
            },
            fallbacks=[CommandHandler('cancel', cancel)],
        )
        
        application.add_handler(conv_handler)
        
        # Start the bot
        await application.initialize()
        await application.start()
        await application.updater.start_polling()
        
        logger.info("ERP Bot is running...")
        
        # Keep running
        await asyncio.Event().wait()
    
    def stop_bot(self):
        """Stop the bot"""
        self.tor_manager.stop_tor()
        logger.info("ERP Bot stopped")

if __name__ == '__main__':
    bot = ERPBot()
    
    try:
        asyncio.run(bot.start_bot())
    except KeyboardInterrupt:
        bot.stop_bot()