from typing import NamedTuple


class TerminalContext(NamedTuple):
	stdout: str 
	prompt: str
	context: str = 'terminal'


class EditorContext(NamedTuple):
	path: str
	content: str
	context: str = 'editor'

