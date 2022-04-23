import asyncio

import discord
from utils import Bot


async def main():
    async with Bot() as bot:
        bot.tree.copy_global_to(guild=discord.Object(id=bot.config["bot"]["id"]))
        await bot.start()


if __name__ == "__main__":
    asyncio.run(main())
