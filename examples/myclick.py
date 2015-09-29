import click

class MyCLI(click.MultiCommand):
    def list_commands(self, ctx):
        cmds = ['hello', 'inout']
        return cmds

    def get_command(self, ctx, name):
        ns = {}
        @click.command()
        @click.option('--count', default=1, help='Number of greetings.')
        def cmd(*args, **kwargs):
            click.echo('hello')
        return cmd

cli = MyCLI(help='This tool\'s subcommands are loaded from a plugin folder dynamically.')

if __name__ == '__main__':
    cli()


