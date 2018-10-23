import pytest
import json
from birdy import import_wps
from birdy import native

# This tests assumes Emu is running on the localhost
url = "http://localhost:5000/wps"


@pytest.mark.online
def test_birdmod():
    m = import_wps(url=url)

    assert m.hello("david") == "Hello david"
    assert (
        m.binaryoperatorfornumbers(inputa=str(1), inputb=str(2), operator="add")
        == "3.0"
    )
    assert m.dummyprocess(10, 20) == ["11", "19"]

    # As reference
    m._convert_objects = False
    out_r, ref_r = m.multiple_outputs(2)
    assert out_r.startswith("http")
    assert out_r.endswith(".txt")
    assert ref_r.startswith("http")
    assert ref_r.endswith(".json")

    # As objects
    m._convert_objects = True
    out_o, ref_o = m.multiple_outputs(2)
    assert out_o == "my output file number 0"
    assert type(ref_o) == dict


@pytest.mark.online
def test_only_one():
    m = import_wps(url=url, processes=["nap"])
    assert count_class_methods(m) == 1

    m = import_wps(url=url, processes="nap")
    assert count_class_methods(m) == 1


@pytest.mark.online
def test_netcdf():

    import netCDF4 as nc

    if nc.getlibversion() > "4.5":
        m = import_wps(url=url, processes=["output_formats"], convert_objects=True)
        ncdata, jsondata = m.output_formats()
        assert isinstance(ncdata, nc.Dataset)
        ncdata.close()
        assert isinstance(jsondata, dict)


def count_class_methods(class_):
    import types

    return len(
        [
            f
            for f in class_.__dict__.values()
            if isinstance(f, types.MethodType) and not f.__name__.startswith("_")
        ]
    )


def test_converter():
    j = native.JSONConverter()
    assert isinstance(j, native.default_converters["application/json"])


def test_jsonconverter():
    d = {"a": 1}
    s = json.dumps(d)

    j = native.JSONConverter()
    assert j.convert_data(s) == d
