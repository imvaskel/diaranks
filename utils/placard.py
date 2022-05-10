from __future__ import annotations

import asyncio
from io import BytesIO
from pathlib import Path
from typing import TYPE_CHECKING

import discord
from discord import Status
from jishaku.functools import executor_function
from PIL import Image, ImageDraw, ImageFont

from .bot import Bot
from .levels import get_level_from_xp, get_level_xp, get_remaining_xp

if TYPE_CHECKING:
    from discord import Member

ASSETS = Path(__file__).parent / "assets"


class Generator:
    background = ASSETS / "card.png"
    presences: dict[Status, Path] = {
        Status.online: ASSETS / "online.png",
        Status.dnd: ASSETS / "dnd.png",
        Status.offline: ASSETS / "offline.png",
        Status.idle: ASSETS / "idle.png"
    }

    ubuntu_b = ASSETS / "Ubuntu-bold.ttf"
    ubuntu_r = ASSETS / "Ubuntu-Regular.ttf"
    font_normal = ImageFont.truetype(str(ubuntu_r), 40)
    font_med = ImageFont.truetype(str(ubuntu_r), 30)
    font_large = ImageFont.truetype(str(ubuntu_b), 42)
    font_small = ImageFont.truetype(str(ubuntu_b), 22)

    @classmethod
    @executor_function
    def generate(
        cls,
        *,
        user: Member,
        level: int,
        current_xp: int,
        user_xp: int,
        next_xp: int,
        user_position: int,
        avatar_bytes: bytes,
    ):
        card = Image.open(cls.background).convert("RGBA")
        avatar = Image.open(BytesIO(avatar_bytes)).convert("RGBA").resize((200, 200))
        status = Image.open(cls.presences[user.status]).convert("RGBA").resize((40, 40))

        profile_pic_holder = Image.new(
            "RGBA", card.size, (155, 155, 155)
        )  # Is used for a blank image so that i can mask

        # Mask to crop image
        mask = Image.new("RGBA", card.size, 0)
        mask = mask.resize(card.size, Image.ANTIALIAS)
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.ellipse(
            [(67, 40), (213.5, 189)], fill=(255, 25, 255, 255)
        )  # The part need to be cropped

        # Editing stuff here
        WHITE = (242, 242, 242)
        DARK = (110, 151, 241)
        YELLOW = (255, 234, 167)

        def get_str(xp):
            if xp < 1000:
                return str(xp)
            if xp >= 1000 and xp < 1000000:
                return str(round(xp / 1000, 1)) + "k"
            if xp > 1000000:
                return str(round(xp / 1000000, 1)) + "M"

        draw = ImageDraw.Draw(card)
        draw.text((290, 79), "Server", WHITE, font=cls.font_med)
        draw.text((299, 109), "Rank", WHITE, font=cls.font_med)
        draw.text((441, 79), "Weekly", WHITE, font=cls.font_med)
        draw.text((455, 109), "Rank", WHITE, font=cls.font_med)
        draw.text((455, 154), "WIP", YELLOW, font=cls.font_normal)
        draw.text(
            (750, 200),
            f"Exp {get_str(user_xp)}/{get_str(next_xp)}",
            WHITE,
            font=cls.font_small,
        )
        draw.text((259, 15), user.name, WHITE, font=cls.font_large)
        draw.text((274, 155), f"#{user_position}", DARK, font=cls.font_normal)
        draw.text((610, 83), f"Level", WHITE, font=cls.font_med)
        draw.text((610, 154), f"{level}", WHITE, font=cls.font_normal)

        # Adding another blank layer for the progress bar
        # Because drawing on card dont make their background transparent
        blank = Image.new("RGBA", card.size, (255, 255, 255, 0))
        blank_draw = ImageDraw.Draw(blank)
        blank_draw.rectangle((0, 250, 900, 230), fill=(7, 7, 7))

        xpneed = next_xp - current_xp
        xphave = user_xp - current_xp

        current_percentage = (xphave / xpneed) * 100
        length_of_bar = (current_percentage * 8) + 80

        blank_draw.rectangle((-1, 230, length_of_bar, 900), fill=DARK)

        profile_pic_holder.paste(avatar, (29, 29, 229, 229))

        pre = Image.composite(profile_pic_holder, card, mask)
        pre = Image.alpha_composite(pre, blank)

        # Status badge
        # Another blank
        blank = Image.new("RGBA", pre.size, (255, 255, 255, 0))
        # blank.paste(status, (169, 169))
        blank.paste(status, (184, 159))

        final = Image.alpha_composite(pre, blank)
        final_bytes = BytesIO()
        final.save(final_bytes, "png")
        final_bytes.seek(0)
        return final_bytes


async def generate_placard(member: discord.Member, xp: int, bot: Bot) -> discord.File:
    level = get_level_from_xp(xp)
    remaining_xp = get_remaining_xp(xp)

    fp = await Generator.generate(
        user=member,
        level=level,
        current_xp=0,
        user_xp=remaining_xp,
        next_xp=get_level_xp(level + 1),
        user_position=bot.get_user_position(member.id),
        avatar_bytes=await member.display_avatar.read()
    )

    return discord.File(fp=fp, filename=f"{member.id}-rank.png")
