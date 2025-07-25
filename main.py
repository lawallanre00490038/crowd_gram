import asyncio

from src.handlers.admin_routes import admin
from src.handlers.auth_routes import auth
from src.handlers.community_routes import broadcast, community
from src.handlers.errors_routes import errors
from src.handlers.onboarding_routes import onboarding, quiz
from src.handlers.payment_routes import payments
from src.handlers.task_routes import tasks
from src.loader import create_bot


async def main():
    bot, dp = create_bot()

    # Register routers
    #add router for login 
    dp.include_router(auth.router) 
    dp.include_router(onboarding.router)
    dp.include_router(quiz.quiz_router)
    dp.include_router(tasks.router)
    dp.include_router(payments.router)
    dp.include_router(community.router)
    dp.include_router(admin.router)
    dp.include_router(errors.router)

    await bot.delete_webhook(drop_pending_updates=True)
    print("✅ Bot is running... Press Ctrl+C to stop.")
    _ = asyncio.create_task(coro=community.start_community_background_tasks())
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())

if __name__ == "__main__":
    asyncio.run(main())
