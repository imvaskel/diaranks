import discord
from discord.ext import commands

class ListenerCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        await self.bot.db.execute("INSERT OR IGNORE INTO ranks(userId) VALUES(?)", (member.id,))
        cursor = await self.bot.db.execute("SELECT * FROM ranks WHERE userId = ?", (member.id,))
        row = await cursor.fetchone()

        self.bot.ranks.update({row[0]: row[1]})

def setup(bot):
    bot.add_cog(ListenerCog(bot))
