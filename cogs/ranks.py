import functools
import io
import discord
from discord.ext import commands, tasks
import random
from disrank.generator import Generator
import asyncio

class RanksCog(commands.Cog, name = "Ranks"):
    def __init__(self, bot):
        self.bot = bot
        self.update_db.start()

    def cog_unload(self):
        self.update_db.cancel()

    def get_card(self, args):
        image = Generator().generate_profile(**args)
        return image

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

    #@commands.command()
    #async def rank(self, ctx, user: discord.Member = None):
        #user = user or ctx.author

        #xp = divmod(self.bot.ranks[user.id], 500)

        #embed = discord.Embed(title=f"{str(user)}'s rank", color = 0x2F3136)
        #embed.add_field(name = "Level", value = xp[0])
        #embed.add_field(name = "XP", value = self.bot.ranks[user.id] or None, inline=False)

        #await ctx.send(embed = embed)

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
    async def rank(self, ctx, member: discord.Member = None):
        if member is None:
            member = ctx.author

        xp = divmod(self.bot.ranks[member.id], 500)
        args = {
            'bg_image': '',
            'profile_image': str(member.avatar_url_as(format='png')),
            'level': xp[0],
            'current_xp': 0,
            'user_xp': xp[1],
            'next_xp': 500,
            'user_position': 1,
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

        await ctx.send(embed = discord.Embed(title = f"Successfully initialized {counter} users"))



def setup(bot):
    bot.add_cog(RanksCog(bot))