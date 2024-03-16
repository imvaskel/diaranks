import asyncio

import asyncpg

from utils import Bot


async def main() -> None:
    async with Bot() as bot, asyncpg.create_pool(**bot.config["bot"]["database"]) as pool:
        bot.db = pool
        await bot.start()


if __name__ == "__main__":
    asyncio.run(main())
