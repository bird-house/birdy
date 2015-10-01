import inspect
import click
from click.core import Option, Command
#from click.decorators import _param_memo

def _make_command(f, name, attrs, cls):
    if isinstance(f, Command):
        raise TypeError('Attempted to convert a callback into a '
                        'command twice.')
    try:
        params = f.__click_params__
        params.reverse()
        del f.__click_params__
    except AttributeError:
        params = []
    help = attrs.get('help')
    if help is None:
        help = inspect.getdoc(f)
        if isinstance(help, bytes):
            help = help.decode('utf-8')
    else:
        help = inspect.cleandoc(help)
    attrs['help'] = help
    return cls(name=name or f.__name__.lower(),
               callback=f, params=params, **attrs)


def _param_memo(f, param):
    if isinstance(f, Command):
        f.params.append(param)
    else:
        if not hasattr(f, '__click_params__'):
            f.__click_params__ = []
        f.__click_params__.append(param)


def option(*param_decls, **attrs):
    """Attaches an option to the command.  All positional arguments are
    passed as parameter declarations to :class:`Option`; all keyword
    arguments are forwarded unchanged (except ``cls``).
    This is equivalent to creating an :class:`Option` instance manually
    and attaching it to the :attr:`Command.params` list.

    :param cls: the option class to instantiate.  This defaults to
                :class:`Option`.
    """
    def decorator(f):
        print "orig attrs", attrs
        if 'help' in attrs:
            attrs['help'] = inspect.cleandoc(attrs['help'])
        OptionClass = attrs.pop('cls', Option)
        print "param_decls", param_decls
        print "attrs", attrs
        print "option", OptionClass
        _param_memo(f, OptionClass(param_decls, **attrs))
        return f
    return decorator

class MyCLI(click.MultiCommand):
    def list_commands(self, ctx):
        cmds = ['hello', 'inout']
        return cmds

    def get_command(self, ctx, name):
        #@click.command()
        #@option("--count", help="no help")
        def mycmd(*args, **kwargs):
            click.echo(name)
        opt = Option(("--count",), {'help': "no help"})
        #cmd.params.append(opt)
        params = []
        #attrs = {'help': 'need more help'}
        attrs = {}
        cmd = Command(name, mycmd, params, **attrs)
        if not hasattr(cmd, '__click_params__'):
            cmd.__click_params__ = []
        cmd.__click_params__.append(option)
        
        return cmd

cli = MyCLI(help='This tool\'s subcommands are loaded dynamically.')

if __name__ == '__main__':
    cli()


