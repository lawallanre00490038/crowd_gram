import asyncio
from loguru import logger

from src.middlewares.logging import LatencyMiddleware, LoggingMiddleware, monitor_resources
from src.routes.admin_routes import admin
from src.routes.auth_routes import auth_new_api
from src.routes.community_routes import community, support
from src.routes.debug import debug_routes
from src.routes.errors_routes import errors
from src.routes.onboarding_routes import onboarding, quiz
from src.routes.payment_routes import payments
from src.routes.task_routes.api2_task_routes import task_main
from src.routes.task_routes.api2_task_routes.contributors import tasks as contributor_tasks
from src.routes.task_routes.api2_task_routes.reviewers import tasks as reviewer_tasks
from src.routes.status import status

from src.menu.set_menu import set_main_menu
from src.loader import create_bot


async def bot_main():
    bot, dp = await create_bot()

    # Set the menu here
    await set_main_menu(bot)

    dp.include_router(status.router)
    dp.include_router(auth_new_api.router)
    dp.include_router(task_main.router)
    dp.include_router(contributor_tasks.router)
    dp.include_router(reviewer_tasks.router)
    dp.include_router(onboarding.router)
    dp.include_router(quiz.quiz_router)
    dp.include_router(payments.router)
    dp.include_router(community.router)
    dp.include_router(support.router)
    dp.include_router(admin.router)
    dp.include_router(errors.router)
    dp.include_router(debug_routes.router)

    await bot.delete_webhook(drop_pending_updates=True)
    logger.info("✅ Bot is running... Press Ctrl+C to stop.")

    loggingmiddleware = LoggingMiddleware()
    dp.message.middleware(loggingmiddleware)
    dp.callback_query.middleware(loggingmiddleware)
    dp.message.middleware(LatencyMiddleware())

    asyncio.create_task(monitor_resources())
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())

# Run everything
if __name__ == "__main__":
    asyncio.run(bot_main())

    # uvicorn.run(app, host="0.0.0.0", port=10000)
