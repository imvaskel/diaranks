from typing import Optional, cast
import discord
from discord.components import Button
from discord.enums import ButtonStyle
from discord.interactions import Interaction

__all__ = (
    "traceback_maker",
    "Confirm"
)

import traceback

def traceback_maker(exc: Exception) -> str:
    etype = type(exc)
    trace = exc.__traceback__

    lines = traceback.format_exception(etype, exc, trace)

    return "".join(lines)

class Confirm(discord.ui.View):
    def __init__(self, timeout: Optional[float] = 180, *, member: discord.Member):
        super().__init__(timeout=timeout)
        self.member = member

    async def _disable_children(self, interaction: Interaction) -> None:
        for child in self.children:
            assert isinstance(child, discord.ui.Button)
            child.disabled = True
        await interaction.response.edit_message(view=self)

    async def interaction_check(self, interaction: Interaction) -> bool:
        if interaction.user == self.member:
            return True
        await interaction.response.send_message("This is not your button.", ephemeral=True)
        return False

    @discord.ui.button(label="Yes", style=ButtonStyle.green)
    async def yes(self, button: Button, interaction: Interaction) -> None:
        self.confirm = True
        await interaction.response.send_message("Confirmed.", ephemeral=True)
        await self._disable_children(interaction)
        self.stop()

    @discord.ui.button(label="No", style=ButtonStyle.red)
    async def no(self, button: Button, interaction: Interaction) -> None:
        self.confirm = False
        await interaction.response.send_message("Denied.", ephemeral=True)
        await self._disable_children(interaction)
        self.stop()