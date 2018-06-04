import click
from owslib.wps import ComplexDataInput
from birdy.utils import is_url


class ComplexParamType(click.ParamType):
    name = 'complex'

    def convert(self, value, param, ctx):
        try:
            if not is_url(value):
                raise ValueError()
            return ComplexDataInput(value)
        except ValueError:
            self.fail('%s is not a valid URL' % value, param, ctx)

    def __repr__(self):
        return 'COMPLEX'


COMPLEX = ComplexParamType()
