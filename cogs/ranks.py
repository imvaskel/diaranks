import functools
import io
import discord
from discord.ext import commands, tasks
from discord.ext.commands.cooldowns import BucketType
import random
from disrank.generator import Generator
import asyncio
import operator



class RanksCog(commands.Cog, name = "Ranks"):
    def __init__(self, bot):
        self.bot = bot
        self.update_db.start()

    def cog_unload(self):
        self.update_db.cancel()

    def get_card(self, args):
        image = Generator().generate_profile(**args)
        return image

    def get_rank(self, userId) -> int:
        """Gets the users rank in the guild leaderboard"""
        sorted_d = dict(sorted(self.bot.ranks.items(), key=operator.itemgetter(1), reverse=True))
        a = [{i: self.bot.ranks[i]} for i in sorted_d]
        for index, entry in enumerate(a):
            if set(entry.keys()) == {userId}:
                return index + 1

    @tasks.loop(minutes = 10)
    async def update_db(self):
        count = 0
        for entry in self.bot.ranks.keys():
            await self.bot.db.execute("INSERT OR REPLACE INTO ranks(userId, xp) VALUES(?, ?)",
                                      (entry, self.bot.ranks[entry]))
            await self.bot.db.commit()
            count += 1
        print(f"Updated the db for {count} users.")

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
        """Updates the cache, owner only."""
        count = 0
        cursor = await self.bot.db.execute("SELECT * FROM ranks")
        for entry in await cursor.fetchall():
            self.bot.ranks[entry[0]] = entry[1]
            count += 1
        await ctx.send(f"Updated the cache for {count} users.")

    @commands.command()
    @commands.cooldown(1, 5, BucketType.user)
    async def rank(self, ctx, *, member: discord.Member = None):
        """Returns the users rank placard, each level is 100 xp"""
        if member is None:
            member = ctx.author

        position = self.get_rank(member.id)

        xp = divmod(self.bot.ranks[member.id], 100)
        args = {
            'bg_image': '',
            'profile_image': str(member.avatar_url_as(format='png')),
            'level': xp[0],
            'current_xp': 0,
            'user_xp': xp[1],
            'next_xp': 500,
            'user_position': position,
            'user_name': str(member),
            'user_status': member.status.name,
        }

        func = functools.partial(self.get_card, args)
        image = await asyncio.get_event_loop().run_in_executor(None, func)

        file = discord.File(fp=image, filename='image.png')
        await ctx.send(file=file)

    @commands.command()
    @commands.has_permissions(manage_guild = True)
    async def reset_ranks(self, ctx):
        await ctx.send("Are you sure you want to reset the ranks? \n**Confirm for yes**")

        def check(message, user):
            return user == ctx.author and message.content.lower == "confirm"

    @commands.command()
    @commands.has_permissions(manage_guild = True)
    async def initialize(self, ctx):
        counter = 0
        for member in ctx.guild.members:
            await self.bot.db.execute("INSERT OR IGNORE INTO ranks(userId) VALUES(?)", (member.id,))
            await self.bot.db.commit()
            counter += 1

        e = await self.bot.get_ranks()
        self.bot.ranks = e
        await ctx.send(embed = discord.Embed(title = f"Successfully initialized {counter} users", color = self.bot.embed_color))



def setup(bot):
    bot.add_cog(RanksCog(bot))