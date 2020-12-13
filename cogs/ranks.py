import discord
from discord.ext import commands, tasks
import random

def calculate_rank(xp):
    rank = xp % 500
    if rank < 1:
        rank = 0
    return rank

class RanksCog(commands.Cog, name = "Ranks"):
    def __init__(self, bot):
        self.bot = bot
        self.update_db.start()

    @tasks.loop(minutes = 10)
    async def update_db(self):
        count = 0
        for entry in self.bot.ranks.keys():
            await self.bot.db.execute("INSERT OR REPLACE INTO ranks(userId, xp) VALUES(?, ?)",
                                      (entry, self.bot.ranks[entry]))
            await self.bot.db.commit()
            count += 1
        print(f"Updated the db for {count} users.")

    @commands.Cog.listener()
    async def on_message(self, message):
        if not message.author.bot:
            self.bot.ranks[message.author.id] += random.randrange(1, 6)

    @commands.command()
    async def rank(self, ctx, user: discord.Member = None):
        user = user or ctx.author

        embed = discord.Embed(title=f"{str(user)}'s rank")
        embed.add_field(name = "Level", value = calculate_rank(self.bot.ranks[user.id]))
        embed.add_field(name = "XP", value = self.bot.ranks[user.id] or None, inline=False)

        await ctx.send(embed = embed)

    @commands.command()
    @commands.is_owner()
    async def update(self, ctx):
        """Updates the DB, owner only."""
        count = 0
        for entry in self.bot.ranks.keys():
            await self.bot.db.execute("INSERT OR REPLACE INTO ranks(userId, xp) VALUES(?, ?)", (entry, self.bot.ranks[entry]))
            await self.bot.db.commit()
            count += 1
        await ctx.send(f"Updated the db for {count} users.")

    @commands.command()
    @commands.is_owner()
    async def update_cache(self, ctx):
        """Updates the DB, owner only."""
        count = 0
        cursor = await self.bot.db.execute("SELECT * FROM ranks")
        for entry in await cursor.fetchall():
            self.bot.ranks[entry[0]] = entry[1]
            count += 1
        await ctx.send(f"Updated the cache for {count} users.")


def setup(bot):
    bot.add_cog(RanksCog(bot))