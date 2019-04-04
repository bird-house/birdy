import datetime
import os
import pytest
import json
# from owslib import crs

from pathlib import Path
from birdy.client import converters, nb_form
from birdy.client.utils import is_embedded_in_request
from birdy import WPSClient
from io import StringIO, BytesIO
import tempfile


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
def test_wps_nb_form(wps):
    for pid in wps._processes.keys():
        if pid in ['bbox', ]:  # Unsupported
            continue
        nb_form(wps, pid)


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
    [meta, ] = resp.get()
    assert meta.startswith("http")
    assert meta.endswith(".metalink")

    # As objects
    [files, ] = resp.get(asobj=True)
    assert len(files) == 2


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
        resp._converters = []
        out = resp.get(asobj=True)
        assert out.output.startswith('http://')


@pytest.mark.online
def test_asobj_non_pythonic_id(wps):
    import json
    d = {'a': 1}
    resp = wps.non_py_id(input_1=1, input_2=json.dumps(d))
    out = resp.get(asobj=True)
    assert out.output_1 == 2
    assert out.output_2 == d


@pytest.mark.skip
def test_esgfapi(wps):
    from owslib_esgfwps import Domain, Dimension, Variable

    uri = data_path("test.nc")

    variable = Variable(var_name='meantemp', uri=uri, name='test')
    domain = Domain([Dimension('time', 0, 10, crs='indices')])

    resp = wps.emu_subset(variable=variable, domain=domain)
    out = resp.get(asobj=True)
    assert 'netcdf' in out.ncdump


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
    assert list(expected_netcdf.variables) == list(netcdf.variables)
    assert expected_netcdf.title == netcdf.title

    # bbox = result[-1]
    # assert bbox.crs == crs.Crs("epsg:4326")
    # assert bbox.dimensions == 2


@pytest.mark.online
def test_netcdf(wps):
    import netCDF4 as nc
    from birdy.client.converters import Netcdf4Converter, JSONConverter

    # Xarray is the default converter. Use netCDF4 here.
    if nc.getlibversion() > "4.5":
        m = WPSClient(url=url, processes=["output_formats"], converters=[Netcdf4Converter, JSONConverter])
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


def test_jsonconverter():
    d = {"a": 1}
    s = json.dumps(d)
    b = bytes(s, 'utf8')

    fs = tempfile.NamedTemporaryFile(mode='w')
    fs.write(s)
    fs.file.seek(0)

    fb = tempfile.NamedTemporaryFile(mode='w+b')
    fb.write(b)
    fb.file.seek(0)

    j = converters.JSONConverter(fs.name)
    assert j.convert() == d

    j = converters.JSONConverter(fb.name)
    assert j.convert() == d

    fs.close()
    fb.close()


def test_zipconverter():
    import zipfile
    f = tempfile.mktemp(suffix='.zip')
    zf = zipfile.ZipFile(f, mode='w')

    a = tempfile.NamedTemporaryFile(mode='w', suffix='.json')
    a.write(json.dumps({"a": 1}))
    a.seek(0)

    b = tempfile.NamedTemporaryFile(mode='w', suffix='.csv')
    b.write('a, b, c\n1, 2, 3')
    b.seek(0)

    zf.write(a.name, arcname=os.path.split(a.name)[1])
    zf.write(b.name, arcname=os.path.split(b.name)[1])
    zf.close()

    [oa, ob] = converters.convert(f, path='/tmp')
    assert oa == {"a": 1}
    assert len(ob.splitlines()) == 2


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
