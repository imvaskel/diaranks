import discord
from discord.ext import commands
import asyncio
import aiosqlite

class CustomBot(commands.AutoShardedBot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.loop = asyncio.get_event_loop()
        self.ranks = {}
        self.db = self.loop.run_until_complete(aiosqlite.connect('bot.db'))

        self.loop.run_until_complete(self.db.execute("""
        CREATE TABLE IF NOT EXISTS ranks (
        userID BIGINT PRIMARY KEY,
        xp BIGINT DEFAULT 0);"""))
        self.ranks = self.loop.run_until_complete(self.get_ranks())
        self.loop.run_until_complete(self.initialize_db())
        self.blacklist = self.loop.run_until_complete(self.get_blacklist())
        self.level_roles = self.loop.run_until_complete(self.get_roles())


    async def get_ranks(self):
        ranks = {}
        cursor = await self.db.execute("SELECT * FROM ranks")
        rows = await cursor.fetchall()
        for row in rows:
            ranks.update({row[0]: row[1]})
        return ranks

    async def close(self):
        await super().close()
        await self.db.close()
        await self.update_db()

    async def update_db(self):
        count = 0
        for entry in self.ranks.keys():
            await self.db.execute("INSERT OR REPLACE INTO ranks(userId, xp) VALUES(?, ?)",
                                      (entry, self.ranks[entry]))
            await self.db.commit()
            count += 1
        print(f"Updated the db for {count} users.")

    async def initialize_db(self):
        """Initializes the db tables"""
        await self.db.execute("CREATE TABLE IF NOT EXISTS roles (roleId BIGINT PRIMARY KEY, level INT);")
        await self.db.execute("CREATE TABLE IF NOT EXISTS blacklist (channelId BIGINT PRIMARY KEY);")

    async def get_blacklist(self):
        """Gets the blacklist"""
        cursor = await self.db.execute("SELECT * FROM blacklist")
        return await cursor.fetchall()

    async def get_roles(self):
        """Gets the roles"""
        cursor = await self.db.execute("SELECT * FROM roles")
        return await cursor.fetchall()
