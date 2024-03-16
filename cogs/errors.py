from __future__ import annotations

import logging
import traceback
from typing import TYPE_CHECKING

import discord
from discord.ext import commands
from discord.ext.commands.errors import CommandError

if TYPE_CHECKING:
    from utils import Bot
    from utils.context import Context


class ErrorHandler(commands.Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        self.ignored_errors: tuple[type[Exception]] = (commands.CommandNotFound,)
        self._logger: logging.Logger = logging.getLogger(__name__)

    @commands.Cog.listener()
    async def on_command_error(self, ctx: Context, error: Exception) -> None:
        if isinstance(error, commands.CommandInvokeError):
            error = error.original

        if isinstance(error, self.ignored_errors):
            return

        if isinstance(error, CommandError):
            embed = discord.Embed(description=str(error), color=self.bot.error_color)
            await ctx.reply(embed=embed)

        else:
            embed = discord.Embed(description=("```py" f"\n{error}" "\n```"), color=self.bot.error_color)
            await ctx.reply(embed=embed)
            self._logger.error("".join(traceback.format_tb(error.__traceback__)))


async def setup(bot: Bot) -> None:
    await bot.add_cog(ErrorHandler(bot))
