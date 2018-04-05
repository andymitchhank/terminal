import click


class HelpMessage(Exception):
	pass


def print_help(ctx, param, value):
	if value:
		raise HelpMessage(ctx.get_help())


def help_option(*param_decls, **attrs):
    """Taken and modified from click decorators to work with Flask"""
    def decorator(f):
        attrs.setdefault('is_flag', True)
        attrs.setdefault('expose_value', False)
        attrs.setdefault('help', 'Show this message and exit.')
        attrs.setdefault('is_eager', True)
        attrs['callback'] = print_help
        return click.decorators.option(*(param_decls or ('--help','-h')), **attrs)(f)
    return decorator


