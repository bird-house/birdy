# noqa: D100

import json
import os
import tempfile

import pytest

from birdy.client import converters


@pytest.fixture
def nc_ex(tmp_path):
    """Test netCDF dataset."""
    import netCDF4 as nc

    fn = tmp_path / "a.nc"
    ds = nc.Dataset(fn, "w")
    ds.createDimension("time", 10)
    ds.createVariable("time", "f8", ("time",))
    ds.close()
    return fn, ds


@pytest.fixture(params=[True, False])
def json_ex(request, tmp_path):
    binary = request.param
    fn = tmp_path / "a.json"
    d = {"a": 1}
    val = json.dumps(d)

    mode = "wb" if binary else "w"
    val = bytes(val, "utf8") if binary else val

    with open(fn, mode) as f:
        f.write(val)

    return fn, d


@pytest.fixture
def txt_ex(tmp_path):
    fn = tmp_path / "a.txt"
    text = "coucou"

    with open(fn, "w") as f:
        f.write(text)
    return fn, text


def test_all_subclasses():  # noqa: D103
    c = converters.all_subclasses(converters.BaseConverter)
    assert converters.MetalinkConverter in c


def test_jsonconverter(json_ex):  # noqa: D103
    fn, d = json_ex

    c = converters.JSONConverter(fn)
    assert c.convert() == d
    assert c.load() == d


def test_geojsonconverter(json_ex):  # noqa: D103
    fn, d = json_ex

    c = converters.GeoJSONConverter(fn)
    assert c.convert() == d
    assert c.load() == d


def test_textconverter(txt_ex):
    fn, text = txt_ex
    t = converters.TextConverter(fn)
    assert t.convert() == text

    assert t.load() == text

    # As class method
    class A:
        def __init__(self):
            self.load = t._load_func()

    a = A()
    assert a.load(encoding="utf8") == text


def test_zipconverter():  # noqa: D103
    import zipfile

    f = tempfile.mktemp(suffix=".zip")
    zf = zipfile.ZipFile(f, mode="w")

    a = tempfile.NamedTemporaryFile(mode="w", suffix=".json")
    a.write(json.dumps({"a": 1}))
    a.seek(0)

    b = tempfile.NamedTemporaryFile(mode="w", suffix=".csv")
    b.write("a, b, c\n1, 2, 3")
    b.seek(0)

    zf.write(a.name, arcname=os.path.split(a.name)[1])
    zf.write(b.name, arcname=os.path.split(b.name)[1])
    zf.close()

    z = converters.ZipConverter(f)
    files = z.convert()
    assert len(files) == 2
    files = z.load()
    assert len(files) == 2
    [oa, ob] = [converters.convert(f, path="/tmp") for f in files]
    assert oa == {"a": 1}
    assert len(ob.splitlines()) == 2

    [oa, ob] = converters.convert(f, path="/tmp", converters=[converters.ZipConverter])
    assert oa == {"a": 1}
    assert len(ob.splitlines()) == 2


def test_geotiff_converter(tmp_path):
    c = converters.GeotiffRasterioConverter("resources/Olympus.tif")
    assert c.load().shape == (1, 99, 133)


def test_jpeg_imageconverter():  # noqa: D103
    # Note: Since the format is not supported, bytes will be returned
    fn = tempfile.mktemp(suffix=".jpeg")
    with open(fn, "w") as f:
        f.write(
            "jpeg.jpg JPEG 1x1 1x1+0+0 8-bit Grayscale Gray 256c 107B 0.000u 0:00.000"
        )

    b = converters.convert(fn, path="/tmp")
    assert isinstance(b, bytes)


def test_netcdf_converter(nc_ex):
    pytest.importorskip("netCDF4")

    fn, ds = nc_ex

    c = converters.Netcdf4Converter(fn)
    ds = c.convert()
    assert "time" in ds.variables


def test_xarray_converter(nc_ex):
    pytest.importorskip("xarray")

    fn, ds = nc_ex

    c = converters.XarrayConverter(fn)
    ds = c.convert()
    assert "time" in ds.variables
