from __future__ import annotations

import traceback
import logging
from typing import TYPE_CHECKING, Tuple

from discord.ext.commands.errors import CommandError

import discord
from discord.ext import commands

if TYPE_CHECKING:
    from utils import Bot

class ErrorHandler(commands.Cog):

    def __init__(self, bot: Bot):
        self.bot = bot
        self.ignored_errors: Tuple[Exception] = (commands.CommandNotFound, )
        self._logger: logging.Logger = logging.getLogger(__name__)

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error: CommandError):
        error = getattr(error, "original", error) # Unpack the error

        if isinstance(error, self.ignored_errors):
            return

        if isinstance(error, CommandError):
            embed = discord.Embed(description=str(error), color=self.bot.error_color)
            await ctx.reply(embed=embed)

        else:
            embed = discord.Embed(description=(
                    "```py"
                    f"\n{error}"
                    "\n```"
                ),
                color=self.bot.error_color
            )
            await ctx.reply(embed=embed)
            self._logger.error(''.join(traceback.format_tb(error.__traceback__)))

def setup(bot: Bot):
    bot.add_cog(ErrorHandler(bot))
