# noqa

from pathlib import Path

from birdy import utils

from .common import resource_file


def test_is_url():  # noqa: D103
    assert utils.is_url("http://localhost:5000/wps")
    assert utils.is_url("file:///path/to/my/file.txt")
    assert not utils.is_url("myfile.txt")


def test_is_file():  # noqa: D103
    assert not utils.is_file(None)
    assert utils.is_file(resource_file("dummy.nc"))
    long_str = "".join("a" for i in range(260))
    assert not utils.is_file(long_str)
    assert utils.is_file(Path(resource_file("dummy.nc")))


def test_sanitize():  # noqa: D103
    assert utils.sanitize("output") == "output"
    assert utils.sanitize("My Output 1") == "my_output_1"
    assert utils.sanitize("a.b") == "a_b"
    assert utils.sanitize("a-b") == "a_b"
    assert utils.sanitize("return") == "return_"
    assert utils.sanitize("Finally") == "finally_"


def test_delist():  # noqa: D103
    assert utils.delist(["one", "two"]) == ["one", "two"]
    assert utils.delist(["one"]) == "one"
    assert utils.delist("one") == "one"


class TestEncode:  # noqa: D101
    nc = resource_file("dummy.nc")
    xml = resource_file("wps_emu_caps.xml")

    def test_str(self):  # noqa: D102
        s = "just a string"
        assert utils.embed(s) == (s, "utf-8")

    def test_local_fn(self):  # noqa: D102
        nc, enc = utils.embed(self.nc, "application/x-netcdf")
        assert isinstance(nc, bytes)
        assert enc == "base64"

        xml, enc = utils.embed(self.xml, "text/xml")
        assert isinstance(xml, str)
        assert enc == "utf-8"

    def test_local_uri(self):  # noqa: D102
        xml, enc = utils.embed("file://" + self.xml, "text/xml")
        assert isinstance(xml, str)

    def test_path(self):  # noqa: D102
        p = Path(self.nc)

        nc, enc = utils.embed(p, "application/x-netcdf")
        assert isinstance(nc, bytes)

    def test_file(self):  # noqa: D102
        with open(self.nc, "rb") as fp:
            nc, enc = utils.embed(fp, "application/x-netcdf")
            assert isinstance(nc, bytes)


class TestGuessType:  # noqa: D101
    def test_zip(self):  # noqa: D102
        mime, enc = utils.guess_type(
            "LSJ_LL.zip",
            ["application/gml+xml", "application/zip", "application/x-zipped-shp"],
        )
        assert mime == "application/zip"

        mime, enc = utils.guess_type(
            "LSJ_LL.zip",
            ["application/gml+xml", "application/x-zipped-shp"],
        )
        assert mime == "application/x-zipped-shp"

    def test_nc(self):  # noqa: D102
        mime, enc = utils.guess_type(
            "https://remote.org/thredds/dodsC/a.nc",
            ["application/x-netcdf", "application/x-ogc-dods"],
        )
        assert mime == "application/x-ogc-dods"

        mime, enc = utils.guess_type(
            "https://remote.org/thredds/file/a.nc",
            ["application/x-ogc-dods", "application/x-netcdf"],
        )
        assert mime == "application/x-netcdf"

    def test_path(self):  # noqa: D102
        from pathlib import Path

        mime, enc = utils.guess_type(
            Path("shape.json"), ["wrong", "application/geo+json"]
        )
        assert mime == "application/geo+json"

        mime, enc = utils.guess_type(
            Path("data.nc"), ["application/x-ogc-dods", "application/x-netcdf"]
        )
        assert mime == "application/x-netcdf"

        mime, enc = utils.guess_type(
            Path("file:///dodsC/data.nc"),
            ["application/x-netcdf", "application/x-ogc-dods"],
        )
        assert mime == "application/x-ogc-dods"
