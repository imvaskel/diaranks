from __future__ import annotations
from typing import TYPE_CHECKING

import discord
from discord.ext import commands
from discord.ext.commands.context import Context

if TYPE_CHECKING:
    from utils import Bot

class OwnerCog(commands.Cog, name="Owner"):
    def __init__(self, bot: Bot):
        self.bot = bot

    @commands.is_owner()
    @commands.command()
    async def update_db(self, ctx: Context):
        async with self.bot.db.acquire() as conn:
            for entry in self.bot.xp.items():
                user, xp = entry
                await conn.execute("INSERT INTO levels(id, xp) VALUES($1, $2) ON CONFLICT (id) DO UPDATE SET xp = $2", user, xp)

def setup(bot):
    bot.add_cog(OwnerCog(bot))
