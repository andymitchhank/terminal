import click

import click_utils


__all__ = ['echo', 'help']


@click.command()
@click_utils.help_option()
@click.pass_context
def help(ctx):
	""" Help text for the applicaiton. Type 'help' to view this message.

		Available Commands: 
		clear, echo, help	

		Use '[command] --help' for more information on a specific command. 
	"""
	click_utils.print_help(ctx, None, True)


@click.command()
@click_utils.help_option()
@click.argument('text')
def echo(text):
	""" Echo back whatever was passed in. """
	return text
