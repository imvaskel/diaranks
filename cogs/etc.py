import discord
from discord.ext import commands

class EtcCog(commands.Cog, name = "etc"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ping(self, ctx):
        await ctx.send(f"Pong! Latency is `{round(self.bot.latency*1000)}`ms")

    @commands.command()
    async def github(self, ctx):
        """Links to the github"""
        embed = discord.Embed(title = "GitHub", color = self.bot.embed_color)

        embed.add_field(name = "__**Issues**__", value = "https://github.com/ImVaskel/diabetes-discord-rank-bot/issues/new")

        await ctx.send(embed = embed)

def setup(bot):
    bot.add_cog(EtcCog(bot))