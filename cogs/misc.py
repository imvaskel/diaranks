import discord
from discord.ext import commands


class Misc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ping(self, ctx: commands.Context):
        await ctx.send(f"Pong! `**{round(self.bot.latency * 1000)}")

    @commands.command()
    async def github(self, ctx: commands.Context):
        await ctx.send("<github.com/imVaskel/diabetes-discord-rank-bot>")

def setup(bot):
    bot.add_cog(Misc(bot))
