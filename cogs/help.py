import discord
from discord.ext import commands

class MyNewHelp(commands.MinimalHelpCommand):
    #Simple embed help
    async def send_pages(self):
        destination = self.get_destination()
        for page in self.paginator.pages:
            embed = discord.Embed(description=page, color = 0x2F3136)
            await destination.send(embed=embed)

class HelpCog(commands.Cog, name = "Help"):
    def __init__(self, bot):
        self.bot = bot
        bot.help_command = MyNewHelp()

def setup(bot):
    bot.add_cog(HelpCog(bot))