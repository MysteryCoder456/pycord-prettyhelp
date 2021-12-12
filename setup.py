import pathlib
from setuptools import setup

from discord.ext.prettyhelp import __version__

HERE = pathlib.Path(__file__).parent
README = (HERE / "README.md").read_text()

setup(
    name="pycord-prettyhelp",
    author="CodeBoi",
    url="https://github.com/MysteryCoder456/pycord-prettyhelp",
    version=__version__,
    packages=["discord.ext.prettyhelp"],
    license="MIT",
    description="A pretty embeded version of the default help command.",
    long_description=README,
    long_description_content_type="text/markdown",
    install_requires=["py-cord"],
    python_requires=">=3.5.3",
)
