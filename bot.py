import asyncio

from utils import Bot


async def main():
    async with Bot() as bot:
        await bot.start()


if __name__ == "__main__":
    asyncio.run(main())
