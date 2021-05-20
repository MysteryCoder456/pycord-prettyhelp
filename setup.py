import pathlib
from setuptools import setup

from discord.ext.prettyhelp import __version__

HERE = pathlib.Path(__file__).parent
README = (HERE / "README.md").read_text()

setup(
    name="discord-ext-prettyhelp",
    author="Circuit",
    url="https://github.com/CircuitsBots/discord-ext-prettyhelp",
    version=__version__,
    packages=["discord.ext.prettyhelp"],
    license="MIT",
    description="A module for making setup wizards easily.",
    long_description=README,
    long_description_content_type="text/markdown",
    install_requires=["discord.py>=1.2.5"],
    python_requires=">=3.5.3",
)
