# noqa: D100

import json
import os
import tempfile

import pytest
import xarray as xr
from common import resource_file

from birdy.client import converters


def test_all_subclasses():  # noqa: D103
    c = converters.all_subclasses(converters.BaseConverter)
    assert converters.MetalinkConverter in c


def test_jsonconverter():  # noqa: D103
    d = {"a": 1}
    s = json.dumps(d)
    b = bytes(s, "utf8")

    fs = tempfile.NamedTemporaryFile(mode="w")
    fs.write(s)
    fs.file.seek(0)

    fb = tempfile.NamedTemporaryFile(mode="w+b")
    fb.write(b)
    fb.file.seek(0)

    j = converters.JSONConverter(fs.name)
    assert j.convert() == d

    j = converters.JSONConverter(fb.name)
    assert j.convert() == d

    fs.close()
    fb.close()


def test_geojsonconverter():  # noqa: D103
    pytest.importorskip("geojson")
    d = {"a": 1}
    s = json.dumps(d)
    b = bytes(s, "utf8")

    fs = tempfile.NamedTemporaryFile(mode="w")
    fs.write(s)
    fs.file.seek(0)

    fb = tempfile.NamedTemporaryFile(mode="w+b")
    fb.write(b)
    fb.file.seek(0)

    j = converters.GeoJSONConverter(fs.name)
    assert j.convert() == d

    j = converters.GeoJSONConverter(fb.name)
    assert j.convert() == d

    fs.close()
    fb.close()


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

    [oa, ob] = converters.convert(f, path="/tmp", converters=[converters.ZipConverter])
    assert oa == {"a": 1}
    assert len(ob.splitlines()) == 2


def test_jpeg_imageconverter():  # noqa: D103
    # Note: Since the format is not supported, bytes will be returned
    fn = tempfile.mktemp(suffix=".jpeg")
    with open(fn, "w") as f:
        f.write(
            "jpeg.jpg JPEG 1x1 1x1+0+0 8-bit Grayscale Gray 256c 107B 0.000u 0:00.000"
        )

    b = converters.convert(fn, path="/tmp")
    assert isinstance(b, bytes)


def test_raster_tif():
    pytest.importorskip("rioxarray")
    fn = resource_file("Olympus.tif")

    da = converters.convert(fn, path="/tmp")
    assert isinstance(da, xr.DataArray)
