# pycord-prettyhelp

An embed version of the built in help command for discord.py

Inspired by the DefaultHelpCommand that discord.py uses, but revised for embeds and additional sorting on individual pages that can be "scrolled" through with reactions.

Made this fork because the original library was built for discord.py which is no longer maintained.

## Installation

`pip install pycord-prettyhelp`

## Usage

Example of how to use it:

```python
from discord.ext import commands
from discord.ext.prettyhelp import PrettyHelp

bot = commands.Bot(
    command_prefix="!", help_command=PrettyHelp()
)
```

### Added Optional Args

- `color` - Set the default embed color
- `ending_note` - Set the footer of the embed. Ending notes are fed a `commands.Context` (`ctx`) and a `PrettyHelp` (`help`) instance for more advanced customization.
- `index_title` - Set the index page name default is *"Categories"*
- `menu` - set a custom menu for navigating pages. Uses a `pretty_help.PrettyMenu()` instance. Default is `pretty_help.DefaultMenu()`
- `no_category` - Set the name of the page with commands not part of a category. Default is "*No Category*"
- `sort_commands` - Sort commands and categories alphabetically
- `show_index` - Show the index page or not

### pretty_help.DefaultHelp args

- `active_time` - Set the time (in seconds) that the message will be active. Default is 30s
- `page_left` - The emoji to use to page left
- `page_right` - The emoji to use to page right
- `remove` - The emoji to use to remove the help message


By default, the help will just pick a random color on every invoke. You can change this using the `color` argument:

```python

from discord.ext import commands
from discord.ext.prettyhelp import DefaultMenu, PrettyHelp

# ":discord:743511195197374563" is a custom discord emoji format. Adjust to match your own custom emoji.
menu = DefaultMenu(
    page_left="\U0001F44D",
    page_right="👎",
    remove=":discord:743511195197374563",
    active_time=5,
)

# Custom ending note
ending_note = (
    "The ending note from {ctx.bot.user.name}"
    "\nFor command {help.clean_prefix}{help.invoked_with}"
)

bot = commands.Bot(command_prefix="!")

bot.help_command = PrettyHelp(
    menu=menu, ending_note=ending_note
)
```

The basic `help` command will break commands up by cogs. Each cog will be a different page. Those pages can be navigated with
the arrow embeds. The message is unresponsive after 30s of no activity, it'll remove the reactions to let you know.

![example](https://cdn.tixte.com/uploads/circuit.is-from.space/kp330yiqu9a.gif)
