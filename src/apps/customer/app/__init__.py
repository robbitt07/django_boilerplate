from collections import namedtuple

from .command import command

App = namedtuple("App", ["command", "query"])


app = App(command=command, query=None)
