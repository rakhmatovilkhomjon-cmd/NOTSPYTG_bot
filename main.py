import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiohttp import web
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

# Import handlers
from handlers.start import router as start_router
from handlers.menu import router as menu_router
from handlers.order_flow import router as order_router
from handlers.reservations import router as reservations_router
from handlers.profile import router as profile_router
from handlers.admin import router as admin_router
from config import config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


async def on_startup(bot: Bot) -> None:
    """Set webhook on startup"""
    if config.webhook_url:
        webhook_url = f"{config.webhook_url}{config.webhook_path}"
        await bot.set_webhook(webhook_url)
        logger.info(f"Webhook set to {webhook_url}")
    else:
        # Delete webhook if exists (for polling mode)
        await bot.delete_webhook(drop_pending_updates=True)
        logger.info("Webhook deleted, using polling mode")


async def main():
    """Main function to start the bot."""

    # Initialize Bot instance with default bot properties
    bot = Bot(
        token=config.token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )

    # Initialize Dispatcher
    dp = Dispatcher()

    # Register startup function
    dp.startup.register(on_startup)

    # Register routers
    dp.include_router(start_router)
    dp.include_router(menu_router)
    dp.include_router(order_router)
    dp.include_router(reservations_router)
    dp.include_router(profile_router)
    dp.include_router(admin_router)

    # Use webhook mode if WEBHOOK_URL is set (production), otherwise use polling (development)
    if config.webhook_url:
        logger.info("Starting bot in webhook mode...")
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
        logger.info(f"Starting webhook server on port {config.port}")
        web.run_app(app, host="0.0.0.0", port=config.port)
    else:
        logger.info("Starting bot in polling mode...")
        try:
            await dp.start_polling(bot, drop_pending_updates=True)
        except KeyboardInterrupt:
            logger.info("Bot stopped by user")
        except Exception as e:
            logger.error(f"Error occurred: {e}")
        finally:
            await bot.session.close()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot stopped!")