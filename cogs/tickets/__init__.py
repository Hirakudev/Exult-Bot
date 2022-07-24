from typing import TYPE_CHECKING
from .config import TicketsConfig

if TYPE_CHECKING:
    from bot import ExultBot


class Custom(TicketsConfig):
    """Custom Cog"""


async def setup(bot: "ExultBot"):
    await bot.add_cog(Custom(bot))
