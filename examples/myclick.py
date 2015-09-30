import inspect
import click
from click.core import Option
from click.decorators import _param_memo


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
        @click.command()
        #@option("--count", help="no help")
        def cmd(*args, **kwargs):
            click.echo(name)
        opt = Option(("--count",), {'help': "no help"})
        cmd.__click_params__.append(option)
        
        return cmd

cli = MyCLI(help='This tool\'s subcommands are loaded dynamically.')

if __name__ == '__main__':
    cli()


