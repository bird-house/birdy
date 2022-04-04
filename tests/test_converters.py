# noqa: D100

import json
import os
import tempfile

import pytest

from birdy.client import converters


@pytest.fixture
def nc_ds(tmp_path):
    """Test netCDF dataset."""
    import netCDF4 as nc

    fn = tmp_path / "a.nc"
    ds = nc.Dataset(fn, "w")
    ds.createDimension("time", 10)
    time = ds.createVariable("time", "f8", ("time",))
    ds.close()
    return fn, ds


def test_all_subclasses():  # noqa: D103
    c = converters.all_subclasses(converters.BaseConverter)
    assert converters.MetalinkConverter in c


def test_jsonconverter(tmp_path):  # noqa: D103
    fs = tmp_path / "s.json"
    fb = tmp_path / "b.json"

    d = {"a": 1}
    s = json.dumps(d)
    b = bytes(s, "utf8")

    with open(fs, "w") as f:
        f.write(s)

    with open(fb, "wb") as f:
        f.write(b)

    js = converters.JSONConverter(fs)
    assert js.convert() == d

    jb = converters.JSONConverter(fb)
    assert jb.convert() == d

    assert js.load() == d
    assert jb.load() == d


def test_textconverter(tmp_path):
    fn = tmp_path / "a.txt"
    text = "coucou"

    with open(fn, "w") as f:
        f.write(text)

    t = converters.TextConverter(fn)
    assert t.convert() == text

    assert t.load() == text

    # As class method
    class A:
        def __init__(self):
            self.load = t.make_load()

    a = A()
    assert a.load(encoding="utf8") == text


def test_geojsonconverter(tmp_path):  # noqa: D103
    pytest.importorskip("geojson")
    d = {"a": 1}
    s = json.dumps(d)
    b = bytes(s, "utf8")

    with open(fs, "w") as f:
        f.write(s)

    with open(fb, "wb") as f:
        f.write(b)

    js = converters.GeoJSONConverter(fs)
    assert js.convert() == d

    jb = converters.GeoJSONConverter(fb)
    assert jb.convert() == d

    assert js.load() == d
    assert jb.load() == d


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


def test_netcdf_converter(nc_ds):
    fn, ds = nc_ds

    c = converters.Netcdf4Converter(fn)
    ds = c.convert()
    assert "time" in ds.variables


def test_xarray_converter(nc_ds):
    fn, ds = nc_ds

    c = converters.XarrayConverter(fn)
    ds = c.convert()
    assert "time" in ds.variables
