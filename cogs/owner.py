from __future__ import annotations

from typing import TYPE_CHECKING

import discord
import utils
from discord.components import SelectOption
from discord.ext import commands
from discord.ext.commands.errors import ExtensionError

if TYPE_CHECKING:
    from typing import List, Optional

    from discord.ext.commands.cog import Cog
    from discord.interactions import Interaction
    from utils.bot import Bot

NEWLINE = "\n"  # Why f-strings


class CleanupFlags(
    commands.FlagConverter, prefix="/", delimiter="", case_insensitive=True
):
    num: int = 5
    bulk: bool = False


class CogSelectView(discord.ui.View):
    def __init__(self, *, timeout: Optional[float] = 180, bot: Bot):
        super().__init__(timeout=timeout)
        self.bot = bot

    async def interaction_check(self, interaction: Interaction) -> bool:
        if interaction.user.id not in self.bot.owner_ids:
            await interaction.response.send_message(
                "You do not own this bot!", ephemeral=True
            )
            return False
        return True


class CogSelect(discord.ui.Select):

    if TYPE_CHECKING:
        view: CogSelectView

    def __init__(self, cogs: List[Cog]):
        options: list[SelectOption] = [
            SelectOption(label=i.__module__, value=i.__module__) for i in cogs
        ]

        super().__init__(
            placeholder="Pick a cog", options=options, max_values=len(options)
        )

    async def callback(self, interaction: Interaction):
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
    async def dev_group(self, ctx: commands.Context):
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)

    @dev_group.command()
    @commands.is_owner()
    async def reload(self, ctx: commands.Context):
        view = CogSelectView(bot=ctx.bot)
        view.add_item(
            CogSelect(
                [i for i in ctx.bot.cogs.values() if i.__module__ != "jishaku.cog"]
            )
        )

        await ctx.send("Reload Cogs", view=view)

    @dev_group.command()
    @commands.is_owner()
    async def cleanup(self, ctx: commands.Context, *, flags: CleanupFlags):
        num = len(
            await ctx.channel.purge(
                limit=flags.num + 1,
                check=lambda m: m.author == ctx.bot.user,
                bulk=flags.bulk,
            )
        )

        await ctx.reply(
            embed=discord.Embed(
                description=f"\N{THUMBS UP SIGN} Successfully deleted {num}/{flags.num} messages"
            ),
            delete_after=25,
        )

    @dev_group.command()
    @commands.is_owner()
    async def delete(
        self, ctx: commands.Context, message: Optional[discord.PartialMessage] = None
    ):
        """
        Deletes the given message, can also be a reply.
        """
        if not message:
            if ctx.message.reference and ctx.message.reference.cached_message:
                message = ctx.message.reference.cached_message
            else:
                raise commands.BadArgument(
                    "No message given or the message is not cached."
                )

        try:
            await message.delete()
            await ctx.message.add_reaction("\N{THUMBS UP SIGN}")
        except Exception as error:
            embed = discord.Embed(description=f"```py\n{error}```")
            await ctx.reply(embed=embed)

    @dev_group.command(aliases=["shutdown"])
    async def restart(self, ctx: commands.Context):
        view = utils.Confirm(member=ctx.author)
        await ctx.send("Are you sure?", view=view)
        await view.wait()

        if view.confirm:
            await self.bot.close()


async def setup(bot: Bot):
    await bot.add_cog(OwnerCog(bot), guild=discord.Object(id=bot.config["bot"]["id"]))
