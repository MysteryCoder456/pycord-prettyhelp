__all__ = ["PrettyHelp"]

from typing import Any, List, Optional, Union

import discord
from discord.ext import commands
from discord.ext.commands.help import HelpCommand

from .menu import DefaultMenu, PrettyMenu


class Paginator:
    def __init__(self, color, pretty_help: "PrettyHelp"):
        """A class that creates pages for PrettyHelp.
        For internal use only.

        Args:
            color (discord.Color): The color to use for embeds.
            pretty_help (PrettyHelp): The PrettyHelp instance.
        """
        self.pretty_help = pretty_help
        self.ending_note = None
        self.color = color
        self.char_limit = 6000
        self.field_limit = 25
        self.prefix = ""
        self.suffix = ""
        self.usage_prefix = "```"
        self.usage_suffix = "```"
        self.clear()

    def clear(self):
        """Clears the paginator to have no pages."""
        self._pages = []

    def _check_embed(self, embed: discord.Embed, *chars: str):
        """
        Check if the emebed is too big to be sent on discord

        Args:
            embed (discord.Embed): The embed to check

        Returns:
            bool: Will return True if the emebed isn't too large
        """
        check = (
            len(embed) + sum(len(char) for char in chars if char)
            < self.char_limit
            and len(embed.fields) < self.field_limit
        )
        return check

    def _new_page(self, title: str, description: str):
        """
        Create a new page

        Args:
            title (str): The title of the new page

        Returns:
            discord.Emebed: Returns an embed with the title and color set
        """
        embed = discord.Embed(
            title=title, description=description, color=self.color
        )
        self._add_page(embed)
        return embed

    def _add_page(self, page: discord.Embed):
        """
        Add a page to the paginator

        Args:
            page (discord.Embed): The page to add
        """
        page.set_footer(text=self.ending_note)
        self._pages.append(page)

    def add_cog(
        self,
        title: Union[str, commands.Cog],
        commands_list: List[commands.Command],
    ):
        """
        Add a cog page to the help menu

        Args:
            title (Union[str, commands.Cog]): The title of the embed
            commands_list (List[commands.Command]): List of commands
        """
        cog = isinstance(title, commands.Cog)
        if not commands_list:
            return

        page_title = title.qualified_name if cog else title
        embed = self._new_page(
            page_title, (title.description or "") if cog else ""
        )

        self._add_command_fields(embed, page_title, commands_list)

    def _add_command_fields(
        self,
        embed: discord.Embed,
        page_title: str,
        commands: List[commands.Command],
    ):
        """
        Adds command fields to Category/Cog and Command Group pages

        Args:
            embed (discord.Embed): The page to add command descriptions
            page_title (str): The title of the page
            commands (List[commands.Command]): The list of commands for
                the fields
        """
        for command in commands:
            if not self._check_embed(
                embed,
                self.ending_note,
                command.name,
                command.short_doc,
                self.prefix,
                self.suffix,
            ):
                embed = self._new_page(page_title, embed.description)

            embed.add_field(
                name=command.name,
                value=(
                    f'{self.prefix}{command.short_doc or "No Description"}'
                    f'{self.suffix}'
                ),
            )

    @staticmethod
    def __command_info(
        command: Union[commands.Command, commands.Group]
    ) -> str:
        info = ""
        if command.description:
            info += command.description + "\n\n"
        if command.help:
            info += command.help
        if not info:
            info = "None"
        return info

    def add_command(
        self, command: commands.Command, signature: str
    ) -> discord.Embed:
        """
        Add a command help page

        Args:
            command (commands.Command): The command to get help for
            signature (str): The command signature/usage string
        """
        page = self._new_page(
            command.qualified_name,
            f"{self.prefix}{self.__command_info(command)}{self.suffix}" or "",
        )
        if command.aliases:
            aliases = ", ".join(command.aliases)
            page.add_field(
                name=self.pretty_help.aliases_string,
                value=f"{self.prefix}{aliases}{self.suffix}",
                inline=False,
            )
        page.add_field(
            name=self.pretty_help.usage_string,
            value=f"{self.usage_prefix}{signature}{self.usage_suffix}",
            inline=False,
        )
        if self.pretty_help.show_bot_perms:
            try:
                perms = command.callback.__bot_perms__
            except AttributeError:
                pass
            else:
                if perms:
                    page.add_field(
                        name=self.pretty_help.bot_perms_title,
                        value=", ".join(perms),
                        inline=False,
                    )
        if self.pretty_help.show_user_perms:
            try:
                chan_perms = command.callback.__channel_perms__
            except AttributeError:
                pass
            else:
                if chan_perms:
                    page.add_field(
                        name=self.pretty_help.user_channel_perms_title,
                        value=", ".join(chan_perms),
                        inline=False,
                    )
            try:
                guild_perms = command.callback.__guild_perms__
            except AttributeError:
                pass
            else:
                if guild_perms:
                    page.add_field(
                        name=self.pretty_help.user_guild_perms_title,
                        value=", ".join(guild_perms),
                        inline=False,
                    )
        return page

    def add_group(
        self, group: commands.Group, commands_list: List[commands.Command]
    ):
        """
        Add a group help page

        Args:
            group (commands.Group): The command group to get help for
            commands_list (List[commands.Command]): The list of commands in
                the group
        """

        page = self.add_command(
            group, self.pretty_help.get_command_signature(group)
        )

        self._add_command_fields(page, group.name, commands_list)

    def add_index(self, include: bool, title: str, bot: commands.Bot):
        """
        Add an index page to the response of the bot_help command

        Args:
            include (bool): Include the index page or not
            title (str): The title of the index page
            bot (commands.Bot): The bot instance
        """
        if include:
            index = self._new_page(title, bot.description or "")
            self._pages.pop(-1)

            for page_no, page in enumerate(self._pages, start=1):
                index.add_field(
                    name=f"{page_no}) {page.title}",
                    value=(
                        f'{self.prefix}{page.description or "No Description"}'
                        f'{self.suffix}'
                    ),
                )
            index.set_footer(text=self.ending_note)
            self._pages.insert(0, index)
        else:
            self._pages[0].description = bot.description

    @property
    def pages(self):
        """Returns the rendered list of pages."""
        return self._pages


class PrettyHelp(HelpCommand):
    def __init__(
        self,
        color: discord.Color = discord.Color.random(),
        dm_help: Optional[bool] = False,
        menu: PrettyMenu = DefaultMenu(),
        sort_commands: bool = True,
        show_index: bool = True,
        show_bot_perms: bool = False,
        show_user_perms: bool = False,
        bot_perms_title: str = "Required Bot Permissions",
        user_guild_perms_title: str = "Required User Permissions",
        user_channel_perms_title: str =
        "Required User Permissions (channel specific)",
        ending_note: Optional[str] = None,
        index_title: str = "Index",
        no_category: str = "No Category",
        aliases_string: str = "Aliases",
        usage_string: str = "Usage",
        **options: Any,
    ):
        """PrettyHelp constructor.

        Args:
            color (discord.Color, optional):
                The color to use for help embeds. Defaults to
                discord.Color.random().
            dm_help (Optional[bool], optional):
                A tribool for whether the bot should dm help or not. Defaults
                to False.
            menu (PrettyMenu, optional):
                A customizable menu. Defaults to DefaultMenu().
            sort_commands (bool, optional):
                Whether or not commands should be sorted. Defaults to True.
            show_index (bool, optional):
                Whether or not to show the index page. Defaults to True.
            show_bot_perms (bool, optional):
                Whether or not to show required bot permissions. Defaults to
                False.
            show_user_perms (bool, optional):
                Whether or not to show required user permissions. Defaults to
                False.
            bot_perms_title (str, optional):
                The embed field name for required bot permissions. Defaults to
                "Required Bot Permissions".
            user_guild_perms_title (str, optional):
                The embed field name for guild-wide required user permissions.
                Defaults to "Required User Permissions".
            user_channel_perms_title (str, optional):
                The embed field name for channel-specific required user
                permissions. Defaults to "Required User Permissions (channel
                specific)".
            ending_note (Optional[str], optional):
                The ending note to put in the footer of embeds. Defaults to
                None.
            index_title (str, optional):
                The string to use for the index embed title. Defaults to
                "Index".
            no_category (str, optional):
                The string to use for commands not in a cog. Defaults to "No
                Category".
            aliases_string (str, optional):
                The string to use for the aliases field. Defaults to "Aliases".
            usage_string (str, optional):
                The string to use for the usage field. Defaults to "Usage".
        """
        self.color = color
        self.dm_help = dm_help
        self.sort_commands = sort_commands
        self.show_index = show_index
        self.menu = menu
        self.paginator = Paginator(self.color, self)
        self.show_user_perms = show_user_perms
        self.show_bot_perms = show_bot_perms
        self.bot_perms_title = bot_perms_title
        self.user_guild_perms_title = user_guild_perms_title
        self.user_channel_perms_title = user_channel_perms_title
        self.index_title = index_title
        self.no_category = no_category
        self.ending_note = ending_note or ""
        self.usage_string = usage_string
        self.aliases_string = aliases_string

        super().__init__(**options)

    async def prepare_help_command(
        self, ctx: commands.Context, command: commands.Command
    ):
        """Prepares the help command. Desinged for internal call only.

        Args:
            ctx (commands.Context): The context help was invoked in.
            command (commands.Command): The command help was invoked for.

        Raises:
            commands.BotMissingPermissions:
                The bot is missing permissions needed to run the paginator.
        """
        if ctx.guild is not None:
            perms = ctx.channel.permissions_for(ctx.guild.me)
            missing: List[str] = []
            if not perms.embed_links:
                missing.append("Embed Links")
            if not perms.read_message_history:
                missing.append("Read Message History")
            if not perms.add_reactions:
                missing.append("Add Reactions")
            if missing:
                raise commands.BotMissingPermissions(missing)

        self.paginator.clear()
        self.paginator.ending_note = self.get_ending_note()
        await super().prepare_help_command(ctx, command)

    def get_ending_note(self) -> str:
        """Gets the ending note for the bot.

        Returns:
            str: The ending note.
        """
        note = self.ending_note or (
            "Type {ctx.clean_prefix}{help.invoked_with} command for more "
            "info on a command.\nYou can also type {ctx.clean_prefix}"
            "{help.invoked_with} category for more info on a category."
        )
        return note.format(ctx=self.context, help=self)

    async def send_pages(self):
        """Invokes self.menu.send_pages with the list of embeds.
        """
        pages = self.paginator.pages
        destination = self.get_destination()
        await self.menu.send_pages(self.context, destination, pages)

    def get_destination(self) -> discord.abc.Messageable:
        """Gets the destination to send help to.

        Returns:
            discord.abc.Messageable: The destination channel.
        """
        ctx = self.context
        if self.dm_help is True:
            return ctx.author
        else:
            return ctx.channel

    async def send_bot_help(self, mapping: dict):
        """Sends help for the entire bot.
        For internal use only.

        Args:
            mapping (dict): A dictionary of Cogs and Commands.
        """
        bot = self.context.bot
        channel = self.get_destination()
        async with channel.typing():
            mapping = dict((name, []) for name in mapping)
            for cmd in await self.filter_commands(
                bot.commands,
                sort=self.sort_commands,
            ):
                mapping[cmd.cog].append(cmd)
            self.paginator.add_cog(self.no_category, mapping.pop(None))
            sorted_map = sorted(
                mapping.items(),
                key=lambda cg: cg[0].qualified_name
                if isinstance(cg[0], commands.Cog)
                else str(cg[0]),
            )
            for cog, command_list in sorted_map:
                self.paginator.add_cog(cog, command_list)
            self.paginator.add_index(self.show_index, self.index_title, bot)
        await self.send_pages()

    async def send_command_help(self, command: commands.Command):
        """Sends help for a single command.

        Args:
            command (commands.Command): The command to send help for.
        """
        filtered = await self.filter_commands([command])
        if filtered:
            self.paginator.add_command(
                command, self.get_command_signature(command)
            )
            await self.send_pages()

    async def send_group_help(self, group: commands.Group):
        """Sends help for a command group.

        Args:
            group (commands.Group): The command group to send help for.
        """
        async with self.get_destination().typing():
            filtered = await self.filter_commands(
                group.commands, sort=self.sort_commands
            )
            self.paginator.add_group(group, filtered)
        await self.send_pages()

    async def send_cog_help(self, cog: commands.Cog):
        """Sends help for an entire cog.

        Args:
            cog (commands.Cog): The cog to send help for.
        """
        async with self.get_destination().typing():
            filtered = await self.filter_commands(
                cog.get_commands(), sort=self.sort_commands
            )
            self.paginator.add_cog(cog, filtered)
        await self.send_pages()
