import asyncio
import logging
from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

from handlers.start import router as start_router
from handlers.menu import router as menu_router
from handlers.admin import router as admin_router
from config import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def on_startup(bot: Bot) -> None:
    """Set webhook on startup"""
    if config.webhook_url:
        await bot.set_webhook(f"{config.webhook_url}{config.webhook_path}")
        logger.info(f"Webhook set to {config.webhook_url}{config.webhook_path}")

async def main() -> None:
    """Main function for webhook mode"""
    
    # Initialize Bot and Dispatcher
    bot = Bot(
        token=config.token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    
    dp = Dispatcher()
    
    # Register startup function
    dp.startup.register(on_startup)
    
    # Register routers
    dp.include_router(start_router)
    dp.include_router(menu_router)
    dp.include_router(admin_router)
    
    # Create aiohttp application
    app = web.Application()
    
    # Create webhook handler
    webhook_requests_handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
    )
    
    # Register webhook handler
    webhook_requests_handler.register(app, path=config.webhook_path)
    
    # Setup application
    setup_application(app, dp, bot=bot)
    
    # Start server
    web.run_app(app, host=config.webapp_host, port=config.webapp_port)

if __name__ == "__main__":
    asyncio.run(main())