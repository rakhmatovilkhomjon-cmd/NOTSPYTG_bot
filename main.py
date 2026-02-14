import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramConflictError
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

        # Run bot startup (set_webhook) when the web app starts
        async def app_startup(_: web.Application) -> None:
            await on_startup(bot)

        app.on_startup.append(app_startup)

        # Health check for Render and load balancers
        async def health(_: web.Request) -> web.Response:
            return web.Response(text="OK", status=200)

        app.router.add_get("/", health)
        app.router.add_get("/health", health)

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
            # Ensure no webhook is set and drop any pending updates before polling.
            # This helps avoid 'Conflict: terminated by other getUpdates request' caused
            # by leftover webhooks or pending updates on Telegram's side.
            await bot.delete_webhook(drop_pending_updates=True)
            logger.info("Webhook deleted before polling; dropped pending updates")

            await dp.start_polling(bot, drop_pending_updates=True)
        except KeyboardInterrupt:
            logger.info("Bot stopped by user")
        except TelegramConflictError as e:
            # If another getUpdates (polling) client is active, Telegram will return
            # a conflict. Log a helpful message and exit so the process doesn't keep
            # hammering the API with retries.
            logger.error("TelegramConflictError: another getUpdates instance appears to be running.")
            logger.error(str(e))
            logger.error("Make sure only one bot instance is running (scale down other replicas or stop local processes). Exiting.")
            sys.exit(1)
        except Exception as e:
            logger.error(f"Error occurred: {e}")
        finally:
            await bot.session.close()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot stopped!")