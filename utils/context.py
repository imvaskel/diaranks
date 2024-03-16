from typing import TYPE_CHECKING

import discord
from discord.ext import commands

if TYPE_CHECKING:
    from .bot import Bot


class Context(commands.Context["Bot"]):
    pass


class GuildContext(Context):
    guild: discord.Guild
    author: discord.Member
    me: discord.Member
    channel: discord.VoiceChannel | discord.TextChannel | discord.Thread
