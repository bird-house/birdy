import datetime
import os
import pytest
import json
# from owslib import crs

from pathlib import Path
from birdy.client import converters
from birdy.client.utils import is_embedded_in_request
from birdy import WPSClient

# These tests assume Emu is running on the localhost
url = "http://localhost:5000/wps"


def data_path(*args):
    return os.path.join(os.path.dirname(__file__), "resources", *args)


@pytest.fixture(scope="module")
def wps():
    return WPSClient(url=url)


@pytest.mark.online
@pytest.mark.skip("slow")
def test_52north():
    """This WPS server has process and input ids with dots and dashes."""
    url = "http://geoprocessing.demo.52north.org:8080/wps/" \
          "WebProcessingService?service=WPS&version=2.0.0&request=GetCapabilities"
    WPSClient(url)


@pytest.mark.online
@pytest.mark.skip("slow")
def test_flyingpigeon():
    url = 'https://pavics.ouranos.ca/twitcher/ows/proxy/flyingpigeon/wps'
    WPSClient(url)


@pytest.mark.online
def test_wps_client_backward_compability():
    from birdy import BirdyClient
    BirdyClient(url=url)
    from birdy import import_wps
    import_wps(url=url)


@pytest.mark.online
def test_wps_docs(wps):
    assert "Processes" in wps.__doc__


@pytest.mark.online
def test_wps_client_single_output(wps):
    result = wps.hello("david")
    assert result.get()[0] == "Hello david"
    result = wps.binaryoperatorfornumbers(inputa=1, inputb=2, operator="add")
    assert result.get()[0] == 3.0


@pytest.mark.online
def test_wps_interact(wps):
    for pid in wps._processes.keys():
        if pid in ['bbox', ]:  # Unsupported
            continue
        wps.interact(pid)


@pytest.mark.online
def test_wps_client_multiple_output(wps):
    # For multiple outputs, the output is a namedtuple
    result = wps.dummyprocess(10, 20)
    output = result.get()
    assert output[0] == "11"
    assert output[1] == "19"
    assert output.output1 == "11"
    assert output.output2 == "19"


@pytest.mark.online
def test_wps_wordcounter(wps):
    fn = '/tmp/text.txt'
    with open(fn, 'w') as f:
        f.write('Just an example')
    out = wps.wordcounter(text=fn).get(asobj=True)
    assert len(out.output) == 3


@pytest.mark.online
def test_interactive(capsys):
    m = WPSClient(url=url, progress=True)
    assert m.hello("david").get()[0] == "Hello david"
    captured = capsys.readouterr()
    assert captured.out.startswith(str(datetime.date.today()))
    assert m.binaryoperatorfornumbers().get()[0] == 5


@pytest.mark.online
def test_wps_client_complex_output(wps):
    resp = wps.multiple_outputs(2)

    # As reference
    out_r, ref_r = resp.get()
    assert out_r.startswith("http")
    assert out_r.endswith(".txt")

    # As objects
    out_o, ref_o = resp.get(asobj=True)
    assert out_o == "my output file number 0"
    assert isinstance(ref_o, dict)


@pytest.mark.online
def test_process_subset_only_one():
    m = WPSClient(url=url, processes=["nap", "sleep"])
    assert count_class_methods(m) == 2

    m = WPSClient(url=url, processes="nap")
    assert count_class_methods(m) == 1


@pytest.mark.online
def test_process_subset_names():
    with pytest.raises(ValueError, match="missing"):
        WPSClient(url=url, processes=["missing"])
    with pytest.raises(ValueError, match="wrong, process, names"):
        WPSClient(url=url, processes=["wrong", "process", "names"])


@pytest.mark.online
def test_asobj(wps):
    resp = wps.ncmeta(dataset=data_path("dummy.nc"))
    out = resp.get(asobj=True)
    assert 'URL' in out.output  # Part of expected text file content.

    resp = wps.ncmeta(dataset='file://' + data_path("dummy.nc"))
    out = resp.get(asobj=True)
    assert 'URL' in out.output

    with open(data_path("dummy.nc"), 'rb') as fp:
        resp = wps.ncmeta(dataset=fp)
        out = resp.get(asobj=True)
        assert 'URL' in out.output

    # If the converter is missing, we should still get the reference.
    with pytest.warns(UserWarning):
        resp._converters.pop("text/plain")
        out = resp.get(asobj=True)
        assert out.output.startswith('http://')


@pytest.mark.online
def test_inputs(wps):
    import netCDF4 as nc
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
        text="some unsafe text &<",
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
        "some unsafe text &<",
    )
    assert expected == result.get(asobj=True)[:-2]

    expected_netcdf = nc.Dataset(data_path("dummy.nc"))
    netcdf = result.get(asobj=True)[-2]
    assert list(expected_netcdf.dimensions) == list(netcdf.dimensions)
    assert list(expected_netcdf.variables) == list(netcdf.variables)
    assert expected_netcdf.title == netcdf.title

    # bbox = result[-1]
    # assert bbox.crs == crs.Crs("epsg:4326")
    # assert bbox.dimensions == 2


@pytest.mark.online
def test_netcdf(wps):
    import netCDF4 as nc

    if nc.getlibversion() > "4.5":
        m = WPSClient(url=url, processes=["output_formats"])
        ncdata, jsondata = m.output_formats().get(asobj=True)
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
    j = converters.JSONConverter()
    assert isinstance(j, converters.default_converters["application/json"])


def test_jsonconverter():
    j = converters.JSONConverter()

    d = {"a": 1}
    s = json.dumps(d)
    assert j.convert_data(s) == d

    s = b'{"a": 1}'
    assert j.convert_data(s) == d


class TestIsEmbedded():
    remote = 'http://remote.org'
    local = 'http://localhost:5000'
    fn = data_path('dummy.nc')
    path = Path(data_path('dummy.nc'))
    uri = 'file://' + fn
    url = 'http://some.random.site/test.txt'

    def test_string(self):
        assert is_embedded_in_request(self.remote, 'just a string')
        assert is_embedded_in_request(self.local, 'just a string')

    def test_file_like(self):
        import io
        f = io.StringIO()
        f.write(u"just a string")
        f.seek(0)

        assert is_embedded_in_request(self.remote, f)
        assert is_embedded_in_request(self.local, f)

    def test_local_fn(self):
        assert is_embedded_in_request(self.remote, self.fn)
        assert not is_embedded_in_request(self.local, self.fn)

    def test_local_path(self):
        assert is_embedded_in_request(self.remote, self.path)
        assert not is_embedded_in_request(self.local, self.path)

    def test_local_uri(self):
        assert is_embedded_in_request(self.remote, self.uri)
        assert not is_embedded_in_request(self.local, self.uri)

    def test_url(self):
        assert not is_embedded_in_request(self.remote, self.url)
        assert not is_embedded_in_request(self.local, self.url)
