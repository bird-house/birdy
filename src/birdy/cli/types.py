# noqa: D100

import click
from owslib.wps import ComplexDataInput

from birdy.utils import is_url


class ComplexParamType(click.ParamType):  # noqa: D101
    name = "complex"

    def convert(self, value, param, ctx):  # noqa: D102
        try:
            if not is_url(value):
                raise ValueError()
            return ComplexDataInput(value)
        except ValueError:
            self.fail(f"{value} is not a valid URL", param, ctx)

    def __repr__(self):  # noqa: D105
        return "COMPLEX"


COMPLEX = ComplexParamType()
