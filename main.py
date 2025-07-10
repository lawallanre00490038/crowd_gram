import asyncio
from src.handlers.admin_routes import admin
from src.handlers.community_routes import community
from src.handlers.errors_routes import errors
from src.handlers.onboarding_routes import onboarding
from src.handlers.payment_routes import payments
from src.handlers.task_routes import tasks
from src.loader import create_bot
from src.handlers.onboarding_routes import quiz

async def main():
    bot, dp = create_bot()

    # Register routers
    dp.include_router(onboarding.router)
    dp.include_router(quiz.quiz_router)
    dp.include_router(tasks.router)
    dp.include_router(payments.router)
    dp.include_router(community.router)
    dp.include_router(admin.router)
    dp.include_router(errors.router)

    print("✅ Bot is running... Press Ctrl+C to stop.")

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
