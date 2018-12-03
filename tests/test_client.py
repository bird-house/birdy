import datetime
import os
import pytest
import json
import sys
from multiprocessing import Process

from birdy.client import converters
from birdy import WPSClient

url = "http://0.0.0.0:5000/wps"


def data_path(*args):
    return os.path.join(os.path.dirname(__file__), "resources", *args)


@pytest.fixture(scope="module")
def start_emu(request):
    """Starts a single instance of the emu WPS for the duration of the tests"""
    def run():
        from emu.cli import cli
        sys.argv = [sys.executable, 'start', '-b', '0.0.0.0']
        cli()
    p = Process(target=run)
    p.start()
    request.addfinalizer(p.terminate)


@pytest.fixture(scope="module")
def wps(start_emu):
    return WPSClient(url=url)


@pytest.mark.skip
@pytest.mark.online
def test_52north():
    """This WPS server has process and input ids with dots and dashes."""
    url = "http://geoprocessing.demo.52north.org:8080/wps" \
          "WebProcessingService?service=WPS&version=2.0.0&request=GetCapabilities"
    WPSClient(url)


def test_wps_client_backward_compability(start_emu):
    from birdy import BirdyClient
    BirdyClient(url=url)
    from birdy import import_wps
    import_wps(url=url)


def test_wps_docs(wps):
    assert "Processes" in wps.__doc__


def test_wps_client_single_output(wps):
    msg, = wps.hello("david")
    assert msg == "Hello david"
    ans, = wps.binaryoperatorfornumbers(inputa=1, inputb=2, operator="add")
    assert ans == 3.0


def test_wps_interact(wps):
    for pid in wps._processes.keys():
        if pid in ['bbox', ]:  # Unsupported
            continue
        print(pid)
        wps.interact(pid)


def test_wps_client_multiple_output(wps):
    # For multiple outputs, the output is a namedtuple
    out = wps.dummyprocess(10, 20)
    x1, x2 = out
    assert x1 == "11"
    assert x2 == "19"
    assert out.output1 == "11"
    assert out.output2 == "19"


@pytest.mark.online
def test_interactive(capsys, start_emu):
    m = WPSClient(url=url, interactive=True)
    assert m.hello("david").output == "Hello david"
    captured = capsys.readouterr()
    assert captured.out.startswith(str(datetime.date.today()))
    assert m.binaryoperatorfornumbers()[0] == 5


@pytest.mark.skip(reason="Complex Output is not working.")
def test_wps_client_complex_output(wps):
    # As reference
    wps._convert_objects = False
    out_r, ref_r = wps.multiple_outputs(2)
    assert out_r.startswith("http")
    assert out_r.endswith(".txt")
    # TODO: fix ComplexDataInput
    assert ref_r.value.startswith("http")
    assert ref_r.value.endswith(".json")

    # As objects
    wps._convert_objects = True
    out_o, ref_o = wps.multiple_outputs(2)
    assert out_o == "my output file number 0"
    assert isinstance(ref_o, dict)
    wps._convert_objects = False


def test_process_subset_only_one(start_emu):
    m = WPSClient(url=url, processes=["nap"])
    assert count_class_methods(m) == 1

    m = WPSClient(url=url, processes="nap")
    assert count_class_methods(m) == 1


def test_process_subset_names(start_emu):
    with pytest.raises(ValueError, match="missing"):
        WPSClient(url=url, processes=["missing"])
    with pytest.raises(ValueError, match="wrong, process, names"):
        WPSClient(url=url, processes=["wrong", "process", "names"])


def test_inputs(wps):
    import netCDF4 as nc
    wps._convert_objects = True
    time_ = datetime.datetime.now().time()
    date_ = datetime.datetime.now().date()
    datetime_ = datetime.datetime.now()
    result = wps.inout(
        string="test string",
        int=3,
        float=3.5,
        boolean=True,
        angle=67.,
        time=time_.isoformat(),
        date=date_.isoformat(),
        datetime=datetime_.isoformat(sep=" "),
        string_choice="rock",
        string_multiple_choice="sitting duck",
        text="some text",
        dataset="file://" + data_path("dummy.nc"),
    )
    expected = (
        "test string",
        3,
        3.5,
        True,
        67.,
        time_,
        date_,
        datetime_,
        "rock",
        "sitting duck",
        "some text",
    )
    assert expected == result[:-2]

    expected_netcdf = nc.Dataset(data_path("dummy.nc"))
    netcdf = result[-2]
    assert list(expected_netcdf.dimensions) == list(netcdf.dimensions)
    assert list(expected_netcdf.variables) == list(netcdf.variables)
    assert expected_netcdf.title == netcdf.title

    # bbox = result[-1]
    # assert bbox.crs == crs.Crs("epsg:4326")
    # assert bbox.dimensions == 2
    wps._convert_objects = False


@pytest.mark.online
def test_netcdf(wps):
    import netCDF4 as nc

    wps._convert_objects = True
    if nc.getlibversion() > "4.5":
        m = WPSClient(url=url, processes=["output_formats"], convert_objects=True)
        ncdata, jsondata = m.output_formats()
        assert isinstance(ncdata, nc.Dataset)
        ncdata.close()
        assert isinstance(jsondata, dict)
    wps._convert_objects = False


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
    j = converters.JSONConverter()
    assert isinstance(j, converters.default_converters["application/json"])


def test_jsonconverter():
    d = {"a": 1}
    s = json.dumps(d)

    j = converters.JSONConverter()
    assert j.convert_data(s) == d
