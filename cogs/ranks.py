from __future__ import annotations
import logging

from random import randint
from typing import List, TYPE_CHECKING, Tuple

import discord
from discord import member
from discord.ext import commands, menus, tasks
from discord.ext.commands.cog import Cog
from discord.ext.commands.context import Context
from utils import Levelling, generate_placard

if TYPE_CHECKING:
    from utils import Bot

class LeaderboardSource(menus.ListPageSource):
    def __init__(self, data, bot: Bot) -> None:
        super().__init__(data, per_page=10)
        self.bot = bot

    async def format_page(self, menu, entries: List[Tuple[int, int]]):
        offset = menu.current_page * self.per_page

        leaderboard = ""

        for rank, info in enumerate(entries, start = offset):
            user, xp = info

            leaderboard += f"{rank+1}. {self.bot.get_user(user)} XP: {xp}\n"

        return leaderboard


class RankHandler(commands.Cog, name="Ranks"):
    def __init__(self, bot: Bot):
        self.bot = bot

        config = self.bot.config["ranks"]
        self._cd = commands.CooldownMapping.from_cooldown(1.0, config["cooldown"], commands.BucketType.member) # Cooldown handler
        self._min: int = config["min"]
        self._max: int = config["max"]
        self._id: int = config["id"]

        self._logger = logging.getLogger(__name__)

        self.update_db.start()

    def cog_unload(self) -> None:
        self.update_db.cancel()

    @tasks.loop(minutes=5)
    async def update_db(self):
        await self.bot.wait_until_ready()

        async with self.bot.db.acquire() as conn:
            for entry in self.bot.xp.items():
                id, xp = entry
                await conn.execute((
                    "INSERT INTO levels(id, xp) VALUES($1, $2)"
                    "ON CONFLICT (id) DO UPDATE SET xp = $2"
                    ), id, xp
                )

        self._logger.debug(f"Updated Database info for {len(self.bot.xp)} users")

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

        if not message.guild or message.guild.id != self._id:
            return

        if message.author == self.bot.user or message.author.bot:
            return

        bucket = self._cd.get_bucket(message)
        retry_after = bucket.update_rate_limit()
        if retry_after:
            return # User is on cooldown.

        xp = randint(self._min, self._max)

        member = message.author

        try:
            level = Levelling.get_level_from_xp(self.bot.xp[member.id])
            self.bot.xp[member.id] += xp
        except KeyError:
            level = 0 # User doesn't exist, so give them level 0 for checking
            self.bot.xp[member.id] = xp

        if level < Levelling.get_level_from_xp(self.bot.xp[member.id]):
            self.bot.dispatch("level_up", user=message.author)

        self._logger.debug(f"Rewarded {xp} xp to {member}")

    @Cog.listener("on_member_join")
    async def add_member_into_database(self, member: discord.Member):
        if member.guild.id != self._id:
            return

        await self.bot.db.execute("INSERT INTO levels(id) VALUES($1) ON CONFLICT DO NOTHING", member.id)

        if member.id not in self.bot.xp:
            self.bot.xp[member.id] = 0

    @commands.command()
    async def rank(self, ctx: commands.Context, *, member: discord.Member = None):
        member = member or ctx.author

        file = await generate_placard(member, self.bot.xp.get(member.id, 0), self.bot)

        await ctx.send(file=file)

    @commands.command(aliases= ["lb"])
    async def leaderboard(self, ctx: Context):
        await menus.MenuPages(source=LeaderboardSource(self.bot.get_sorted_leaderboard(), self.bot)).start(ctx)

def setup(bot):
    bot.add_cog(RankHandler(bot))
