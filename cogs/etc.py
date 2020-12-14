import discord
from discord.ext import commands

class EtcCog(commands.Cog, name = "etc"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ping(self, ctx):
        await ctx.send(f"Pong! Latency is `{round(self.bot.latency*1000)}`ms")

def setup(bot):
    bot.add_cog(EtcCog(bot))