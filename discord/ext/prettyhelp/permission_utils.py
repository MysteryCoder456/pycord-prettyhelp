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

            def check_wrapper(_func: Command):
                func = (
                    _func if not isinstance(_func, Command) else _func.callback
                )
                to_add = [s.title().replace("_", " ") for s in perms]
                if hasattr(func, attr_name):
                    func.__getattribute__(attr_name).extend(to_add)
                else:
                    func.__setattr__(
                        attr_name, to_add
                    )
                return check(_func)
            return check_wrapper
        return predicate
    return decorator


if not TYPE_CHECKING:
    @store_perms_in_command("__guild_perms__")
    def has_guild_permissions(*args, **kwargs):  # noqa: F811
        return r_has_guild_permissions(*args, **kwargs)

    @store_perms_in_command("__channel_perms__")
    def has_permissions(*args, **kwargs):  # noqa: F811
        return r_has_permissions(*args, **kwargs)

    @store_perms_in_command("__bot_perms__")
    def bot_has_permissions(*args, **kwargs):  # noqa F811
        return r_bot_has_permissions(*args, **kwargs)
