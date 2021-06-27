from __future__ import annotations
import logging

from random import randint
from typing import TYPE_CHECKING

import discord
from discord import member
from discord.ext import commands
from discord.ext.commands.cog import Cog
from utils import Levelling

if TYPE_CHECKING:
    from utils import Bot

class RankHandler(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

        config = self.bot.config["ranks"]
        self._cd = commands.CooldownMapping.from_cooldown(1.0, config["cooldown"], commands.BucketType.member) # Cooldown handler
        self._min: int = config["min"]
        self._max: int = config["max"]
        self._id: int = config["id"]

        self._logger = logging.getLogger(__name__)

    @Cog.listener('on_level_up')
    async def on_level_up(self, user: discord.Member):
        level = Levelling.get_level_from_xp(self.bot.xp[user.id])

        try:
            role_id = self.bot.roles[level]
        except KeyError:
            return # Level doesn't have a role bound to it, so return.

        await user.add_roles(user.guild.get_role(role_id), reason=f"User levelled up.")
        self._logger.debug(f"Gave user {user} role for level {level}.")

    @Cog.listener('on_message')
    async def add_xp(self, message: discord.Message):
        if message.guild.id != self._id or message.author.bot:
            return

        bucket = self._cd.get_bucket(message)
        retry_after = bucket.update_rate_limit()
        if retry_after:
            return # User is on cooldown.

        xp = randint(self._min, self._max)

        try:
            level = Levelling.get_level_from_xp(self.bot.xp[member.id])
            self.bot.xp[member.id] += xp
        except KeyError:
            level = 0 # User doesn't exist, so give them level 0 for checking
            self.bot.xp[member.id] = xp

        if level < Levelling.get_level_from_xp(self.bot.xp[member.id]):
            self.bot.dispatch("level_up", user=message.author)

def setup(bot):
    bot.add_cog(RankHandler(bot))
