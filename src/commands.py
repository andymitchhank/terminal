import click


@click.command()
@click.argument('text')
def echo(text):
	return text
