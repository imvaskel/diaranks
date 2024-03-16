from __future__ import annotations

from typing import TYPE_CHECKING, Literal

import discord
from discord.components import SelectOption
from discord.ext import commands
from discord.ext.commands.errors import ExtensionError

import utils

if TYPE_CHECKING:
    from discord.ext.commands.cog import Cog
    from discord.interactions import Interaction

    from utils import Bot, GuildContext

NEWLINE = "\n"  # Why f-strings


class CleanupFlags(commands.FlagConverter, prefix="/", delimiter="", case_insensitive=True):
    num: int = 5
    bulk: bool = False


class CogSelectView(discord.ui.View):
    def __init__(self, *, timeout: float | None = 180, bot: Bot) -> None:
        super().__init__(timeout=timeout)
        self.bot = bot

    async def interaction_check(self, interaction: Interaction) -> bool:
        if interaction.user.id not in self.bot.owner_ids:
            await interaction.response.send_message("You do not own this bot!", ephemeral=True)
            return False
        return True


class CogSelect(discord.ui.Select):
    if TYPE_CHECKING:
        view: CogSelectView

    def __init__(self, cogs: list[Cog]) -> None:
        options: list[SelectOption] = [SelectOption(label=i.__module__, value=i.__module__) for i in cogs]

        super().__init__(placeholder="Pick a cog", options=options, max_values=len(options))

    async def callback(self, interaction: Interaction) -> None:
        await interaction.response.defer()
        followup = interaction.followup
        for cog in self.values:
            try:
                await self.view.bot.reload_extension(cog)
            except ExtensionError as e:
                await followup.send(
                    f"Failed to reload `{cog}`: \n```py\n{utils.traceback_maker(e)}```",
                    ephemeral=True,
                )
            else:
                await followup.send(f"Reloaded cog `{cog}`", ephemeral=True)


class OwnerCog(commands.Cog, name="owner"):
    """
    Owner commands.
    """

    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @commands.is_owner()
    @commands.hybrid_group(name="dev")
    async def dev_group(self, ctx: GuildContext) -> None:
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)

    @dev_group.command()
    @commands.is_owner()
    async def reload(self, ctx: GuildContext) -> None:
        view = CogSelectView(bot=ctx.bot)
        view.add_item(CogSelect([i for i in ctx.bot.cogs.values() if i.__module__ != "jishaku.cog"]))

        await ctx.send("Reload Cogs", view=view)

    @dev_group.command()
    @commands.is_owner()
    async def cleanup(self, ctx: GuildContext, *, flags: CleanupFlags) -> None:
        num = len(
            await ctx.channel.purge(
                limit=flags.num + 1,
                check=lambda m: m.author == ctx.bot.user,
                bulk=flags.bulk,
            )
        )

        await ctx.reply(
            embed=discord.Embed(description=f"\N{THUMBS UP SIGN} Successfully deleted {num}/{flags.num} messages"),
            delete_after=25,
        )

    @dev_group.command(aliases=["shutdown"])
    @commands.is_owner()
    async def restart(self, ctx: GuildContext) -> None:
        view = utils.Confirm(member=ctx.author)
        await ctx.send("Are you sure?", view=view)
        await view.wait()

        if view.confirm:
            await self.bot.close()

    @dev_group.command()
    @commands.is_owner()
    async def sync(
        self,
        ctx: GuildContext,
        guilds: commands.Greedy[discord.Object],
        spec: Literal["~"] | None = None,
    ) -> None:
        # thank you umbra
        if not guilds:
            if spec == "~":
                fmt = await ctx.bot.tree.sync(guild=ctx.guild)
            else:
                fmt = await ctx.bot.tree.sync()
            await ctx.send(f"Synced {len(fmt)} commands {'globally' if spec is None else 'to the current guild.'}")
            return
        fmt = 0
        for guild in guilds:
            try:
                await ctx.bot.tree.sync(guild=guild)
            except discord.HTTPException:
                pass
            else:
                fmt += 1
        await ctx.send(f"Synced the tree to {fmt}/{len(guilds)} guilds.")


async def setup(bot: Bot) -> None:
    await bot.add_cog(OwnerCog(bot))
