import click

import click_utils

__all__ = ['echo']

@click.command()
@click_utils.help_option()
@click.argument('text')
def echo(text):
	""" Echo back whatever was passed in. """
	return text
