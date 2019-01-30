import pytest

import click
from click.testing import CliRunner

from birdy.cli.base import BirdyCLI
from .common import resource_file

XML = open(resource_file('wps_emu_caps.xml'), 'rb').read()


@click.command(cls=BirdyCLI,
               url="http://localhost:5000/wps",
               xml=XML)
def cli():
    pass


@pytest.mark.skip(reason="openssl import issue on travis")
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
@pytest.mark.skip(reason="hidden traceback")
def test_hello_stranger():
    runner = CliRunner()
    result = runner.invoke(cli, ['hello', '--name', 'stranger'])
    assert result.exit_code == 0


@pytest.mark.online
@pytest.mark.skip(reason="hidden traceback")
def test_multiple_outputs():
    runner = CliRunner()
    result = runner.invoke(cli, ['multiple_outputs', '--count 2', ])
    assert result.exit_code == 0
