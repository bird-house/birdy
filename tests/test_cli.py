from click.testing import CliRunner
import pytest

import birdy.cli.run

from .common import EMU_CAPS_XML, URL_EMU


cli = birdy.cli.run.cli
cli.url = URL_EMU
cli.caps_xml = EMU_CAPS_XML


@pytest.mark.online
def test_help():
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "hello" in result.output
    assert "wordcount" in result.output
    assert "language" in result.output
    assert "show-languages" in result.output


@pytest.mark.online
def test_show_languages():
    runner = CliRunner()
    result = runner.invoke(cli, ["--show-languages"])
    assert result.exit_code == 0
    assert "en-US" in result.output


@pytest.mark.online
def test_hello():
    runner = CliRunner()
    result = runner.invoke(cli, ["hello", "--help"])
    assert result.exit_code == 0
    assert "--name" in result.output


@pytest.mark.online
def test_hello_stranger():
    runner = CliRunner()
    result = runner.invoke(cli, ["hello", "--name", "stranger"])
    assert result.exit_code == 0


@pytest.mark.online
@pytest.mark.xfail(reason="click hides exception")
def test_multiple_outputs():
    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "multiple_outputs",
            "--count 2",
        ],
    )
    assert result.exit_code == 0
