"""
Asosiy bot fayli
"""
import asyncio
import logging
import os
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from dotenv import load_dotenv

from handlers import start, tasks, schedule, reminders, stats, tests, admin, settings
from utils.database import init_db
from utils.ai_helper import init_ai
from utils.scheduler import init_scheduler, stop_scheduler

# Environment variables
load_dotenv()

# Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Bot va Dispatcher
bot = None
dp = Dispatcher()

async def main():
    """Asosiy funksiya"""
    global bot
    
    # Bot token tekshirish
    token = os.getenv('BOT_TOKEN')
    if not token:
        logger.error("BOT_TOKEN topilmadi! .env faylini tekshiring.")
        return
    
    bot = Bot(
        token=token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    
    # Database
    logger.info("Database initializing...")
    await init_db()
    logger.info("Database ready!")
    
    # AI
    logger.info("AI initializing...")
    if init_ai():
        logger.info("AI ready!")
    else:
        logger.warning("AI initialization failed. Using fallback methods.")
    
    # Routerlarni qo'shish
    dp.include_router(start.router)
    dp.include_router(admin.router)  # Admin birinchi bo'lishi kerak
    dp.include_router(settings.router)
    dp.include_router(tasks.router)
    dp.include_router(schedule.router)
    dp.include_router(reminders.router)
    dp.include_router(stats.router)
    dp.include_router(tests.router)
    
    # Schedulerni ishga tushirish
    logger.info("Scheduler initializing...")
    init_scheduler(bot)
    logger.info("Scheduler started!")
    
    # Botni ishga tushirish
    logger.info("Bot starting...")
    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        stop_scheduler()
        await bot.session.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot error: {e}")
