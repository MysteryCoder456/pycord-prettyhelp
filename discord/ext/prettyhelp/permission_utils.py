"""
Since commands.has_guild_permissions, commands.has_permissions,
and commands.bot_has_permissions merely add a check instead of
storing the values, the only way for the show_user_perms
and show_bot_perms fields to work is if you use these custom
permission decorators.
"""

from typing import Callable, TYPE_CHECKING

from discord.ext.commands import Command, check
if not TYPE_CHECKING:
    from discord.ext.commands import (
        has_guild_permissions as r_has_guild_permissions,
        has_permissions as r_has_permissions,
        bot_has_permissions as r_bot_has_permissions,
    )
else:
    from discord.ext.commands import (
        has_guild_permissions,
        has_permissions,
        bot_has_permissions,
    )

__all__ = [
    "has_guild_permissions",
    "has_permissions",
    "bot_has_permissions",
]


def store_perms_in_command(attr_name: str):
    def decorator(permission_decorator: Callable[..., check]):
        def predicate(**perms):
            check = permission_decorator(**perms)

            def check_wrapper(func: Command):
                if not isinstance(func, Command):
                    raise RuntimeError(
                        "Do to a discord.py limitation, all permission "
                        "decorators must be put before the command decorator."
                    )
                to_add = [s.title().replace("_", " ") for s in perms]
                if hasattr(func, attr_name):
                    func.__getattribute__(attr_name).extend(to_add)
                else:
                    func.__setattr__(
                        attr_name, to_add
                    )
                return check(func)
            return check_wrapper
        return predicate
    return decorator


if not TYPE_CHECKING:
    @store_perms_in_command("guild_perms")
    def has_guild_permissions(*args, **kwargs):
        return r_has_guild_permissions(*args, **kwargs)

    @store_perms_in_command("channel_perms")
    def has_permissions(*args, **kwargs):
        return r_has_permissions(*args, **kwargs)

    @store_perms_in_command("bot_perms")
    def bot_has_permissions(*args, **kwargs):
        return r_bot_has_permissions(*args, **kwargs)
