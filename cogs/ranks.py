from __future__ import annotations

import logging
from random import randint
from typing import TYPE_CHECKING

import discord
from discord.ext import commands, menus, tasks
from discord.ext.commands.cog import Cog
from discord.ext.menus.views import ViewMenuPages

from utils import generate_placard, get_level_from_xp
from utils.utils import Confirm

if TYPE_CHECKING:
    from utils import Bot
    from utils.context import GuildContext


class FixedViewMenuPages(ViewMenuPages):
    async def send_initial_message(self, ctx: GuildContext, channel: discord.TextChannel) -> None:
        page = await self._source.get_page(0)
        kwargs = await self._get_kwargs_from_page(page)
        return await self.send_with_view(ctx, **kwargs)  # type: ignore


class LeaderboardSource(menus.ListPageSource):
    def __init__(self, data: list[tuple[int, int]], bot: Bot) -> None:
        super().__init__(data, per_page=10)
        self.bot = bot

    async def format_page(self, menu: menus.MenuPages, entries: list[tuple[int, int]]) -> discord.Embed:
        offset = menu.current_page * self.per_page

        leaderboard = ""

        for rank, info in enumerate(entries, start=offset + 1):
            user, xp = info

            leaderboard += f"{rank}. ``{self.bot.get_user(user)}`` XP: ``{xp}``\n"

        return discord.Embed(description=leaderboard)


class RankHandler(commands.Cog, name="Ranks"):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

        config = self.bot.config["ranks"]
        self._cd = commands.CooldownMapping.from_cooldown(1.0, config["cooldown"], commands.BucketType.member)
        self._min: int = config["min"]
        self._max: int = config["max"]
        self._id: int = config["id"]

        self._logger = logging.getLogger(__name__)

    async def cog_load(self) -> None:
        self.update_db.start()

    async def cog_unload(self) -> None:
        self.update_db.cancel()

    @tasks.loop(minutes=5)
    async def update_db(self) -> None:
        await self.bot.wait_until_ready()

        async with self.bot.db.acquire() as conn:
            await conn.executemany(
                ("INSERT INTO LEVELS(id, xp) VALUES($1, $2)" "ON CONFLICT (id) DO UPDATE SET xp = $2"),
                self.bot.xp.items(),
            )

        self._logger.debug("Updated Database info for %s users", len(self.bot.xp))

    @Cog.listener("on_level_up")
    async def on_level_up(self, user: discord.Member) -> None:
        level = get_level_from_xp(self.bot.xp[user.id])

        try:
            role_id = self.bot.roles[level]
        except KeyError:
            return  # Level doesn't have a role bound to it, so return.

        role = user.guild.get_role(role_id)
        if role:
            await user.add_roles(role, reason="User levelled up.")
            self._logger.debug("Gave user %s role for level %s.", user, level)

    @Cog.listener("on_message")
    async def add_xp(self, message: discord.Message) -> None:
        if not message.guild or message.guild.id != self._id:
            return

        if message.author == self.bot.user or message.author.bot:
            return

        if message.channel.id in self.bot.blacklist:
            return

        bucket = self._cd.get_bucket(message)
        if bucket:
            retry_after = bucket.update_rate_limit()
            if retry_after:
                return  # User is on cooldown.

        xp = randint(self._min, self._max)

        member = message.author

        try:
            level = get_level_from_xp(self.bot.xp[member.id])
            self.bot.xp[member.id] += xp
        except KeyError:
            level = 0  # User doesn't exist, so give them level 0 for checking
            self.bot.xp[member.id] = xp

        if level < get_level_from_xp(self.bot.xp[member.id]):
            self.bot.dispatch("level_up", user=message.author)

        self._logger.debug("Rewarded %s xp to %s", xp, member)

    @Cog.listener("on_member_join")
    async def add_member_into_database(self, member: discord.Member) -> None:
        if member.guild.id != self._id:
            return

        await self.bot.db.execute("INSERT INTO levels(id) VALUES($1) ON CONFLICT DO NOTHING", member.id)

        if member.id not in self.bot.xp:
            self.bot.xp[member.id] = 0

    @commands.hybrid_command()
    async def rank(
        self,
        ctx: commands.Context,
        *,
        member: discord.Member = commands.param(default=lambda ctx: ctx.author),
    ) -> None:
        """
        Get a user's rank placard
        """
        async with ctx.typing():
            file = await generate_placard(member, self.bot.xp.get(member.id, 0), self.bot)

        await ctx.send(file=file)

    @commands.hybrid_command(aliases=["lb"])
    async def leaderboard(self, ctx: GuildContext) -> None:
        """Return the leaderboard, with interactive pagination."""
        await ctx.defer()

        await FixedViewMenuPages(source=LeaderboardSource(self.bot.get_sorted_leaderboard(), self.bot)).start(ctx)

    @commands.hybrid_command()
    @commands.guild_only()
    @commands.has_guild_permissions(manage_guild=True)
    async def reset(self, ctx: GuildContext) -> None:
        await ctx.defer()

        confirm = Confirm(member=ctx.author)
        await ctx.send("Confirm.", view=confirm)
        await confirm.wait()
        if not confirm.confirm:
            return

        await self.bot.db.execute("DELETE FROM levels;")
        self.bot.xp = {}
        await ctx.reply("Reset all the ranks!")


async def setup(bot: Bot) -> None:
    await bot.add_cog(RankHandler(bot))
