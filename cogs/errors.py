import discord
from discord.ext import commands

class ErrorsCog(commands.Cog, name = "Errors"):
    #Error handler

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        ignored_errors = (commands.CommandNotFound)
        stringed_errors = (commands.MissingPermissions, commands.MissingRequiredArgument, commands.BadArgument,
                           commands.BotMissingPermissions,
                           discord.NotFound, commands.CommandOnCooldown, commands.BadUnionArgument)

        if isinstance(error, ignored_errors):
            return

        if isinstance(error, stringed_errors):
            await ctx.send(embed=discord.Embed(title=str(error), color=discord.Color.red()))
        elif isinstance(error, commands.NotOwner):
            await ctx.send(embed=discord.Embed(title="You do not own this bot.", color=discord.Color.red()))
        else:
            embed = discord.Embed(title = "An error occurred!",
                                  description = "[Please report this to the bots GitHub with the codeblock's content.](https://github.com/ImVaskel/diabetes-discord-rank-bot)",
                                  color = discord.Color.red(),
                                  timestamp = ctx.message.created_at)
            embed.add_field(name = "Error Details: ",
                            value = f"```py\n{str(error)}```")
            embed.set_footer(text = "That above is a hyperlink to the github, click it!")

            await ctx.send(embed = embed)

def setup(bot):
    bot.add_cog(ErrorsCog(bot))