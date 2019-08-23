import pytest

import click
from click.testing import CliRunner

from birdy.cli.base import BirdyCLI
from .common import (
    URL_EMU,
    EMU_CAPS_XML,
    # EMU_DESC_XML,
)


@click.command(cls=BirdyCLI,
               url=URL_EMU,
               caps_xml=EMU_CAPS_XML,
               # desc_xml=EMU_DESC_XML
               )
def cli():
    pass


def test_help():
    runner = CliRunner()
    result = runner.invoke(cli, ['--help'])
    assert result.exit_code == 0
    assert 'hello' in result.output
    assert 'wordcount' in result.output


@pytest.mark.online
def test_hello():
    runner = CliRunner()
    result = runner.invoke(cli, ['hello', '--help'])
    assert result.exit_code == 0
    assert '--name' in result.output


@pytest.mark.online
def test_hello_stranger():
    runner = CliRunner()
    result = runner.invoke(cli, ['hello', '--name', 'stranger'])
    assert result.exit_code == 0


@pytest.mark.online
@pytest.mark.xfail(reason="click hides exception")
def test_multiple_outputs():
    runner = CliRunner()
    result = runner.invoke(cli, ['multiple_outputs', '--count 2', ])
    assert result.exit_code == 0
