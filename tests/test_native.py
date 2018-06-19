import pytest
import json
from birdy import native_client
from birdy import native

# This tests assumes Emu is running on the localhost
url = "http://localhost:5000/wps"


@pytest.mark.online
def test_birdmod():
    m = native_client(url=url)
    assert m.hello('david') == 'Hello david'
    assert m.binaryoperatorfornumbers(inputa=1, inputb=2, operator='add') == 3.0
    assert m.dummyprocess(10, 20) == ['11', '19']

    txt, ref = m.multiple_outputs(2)

    assert type(txt) == str
    assert type(ref) == str

    m._config.asobject = True
    txt, ref = m.multiple_outputs(2)
    assert type(txt) == str
    assert type(ref) == dict


@pytest.mark.online
def test_only_one():
    m = native_client(url=url, processes=['nap'])
    assert count_mod_func(m) == 1

    m = native_client(url=url, processes='nap')
    assert count_mod_func(m) == 1


@pytest.mark.online
def test_netcdf():

    import netCDF4 as nc
    if nc.getlibversion() > '4.5':
        m = native_client(url=url, processes=['output_formats'], asobject=True)
        ncdata, jsondata = m.output_formats()
        assert isinstance(ncdata, nc.Dataset)
        ncdata.close()
        assert isinstance(jsondata, dict)


def count_mod_func(mod):
    import types
    return len([f for f in mod.__dict__.values() if isinstance(f, types.FunctionType)])


def test_converter():
    j = native.JSONConverter()
    assert j.default == 'json'


def test_jsonconverter():
    d = {"a": 1}
    s = json.dumps(d)

    j = native.JSONConverter()
    assert j.json(s) == d


def test_config():
    c = native.Config()
    c.asobject = 1
    assert c.asobject == True


