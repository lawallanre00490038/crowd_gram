import asyncio

async def schedule_task(interval, coro, *args):
    while True:
        await coro(*args)
        await asyncio.sleep(interval)
