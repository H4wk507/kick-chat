import os

from setuptools import setup


def read_file(fname: str) -> str:
    with open(fname, encoding="utf-8") as f:
        return f.read()


VERSION = "1.0.0"

HERE = os.path.dirname(__file__)

LONG_DESCRIPTION = read_file(os.path.join(HERE, "README.md"))

REQUIREMENTS = read_file(os.path.join(HERE, "requirements.txt")).splitlines()

setup(
    name="kick-chat",
    version=VERSION,
    description="kick.com chat in the terminal",
    author="Piotr Skowroński",
    license="GPLv3",
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    classifiers=[
        "Environment :: Console",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
    ],
    entry_points={
        "console_scripts": [
            "kick-chat=kick_chat.main:main",
        ],
    },
    install_requires=REQUIREMENTS,
    python_requires=">=3.10",
)
