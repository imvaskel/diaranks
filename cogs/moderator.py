import discord
from discord.ext import commands
from discord.ext.commands import Cog

class ModeratorCog(Cog, name = "Moderator"):
    def __init__(self, bot):
        self.bot = bot


def setup(bot):
    bot.add_cog(ModeratorCog(bot))