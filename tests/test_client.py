import datetime
import os
import json
import tempfile
from pathlib import Path
from unittest import mock
import owslib.wps
import pytest

# from owslib import crs

from birdy.client import converters, nb_form
from birdy.client.base import sort_inputs_key
from birdy.client.utils import is_embedded_in_request
from birdy import WPSClient
from .common import (
    resource_file,
    URL_EMU,
    EMU_CAPS_XML,
    EMU_DESC_XML,
)


# 52 north WPS
url_52n = "http://geoprocessing.demo.52north.org:8080/wps/WebProcessingService?service=WPS&version=1.0.0&request=GetCapabilities"  # noqa: E501
# flyingpigeon WPS at Ouranos
url_fly = "https://pavics.ouranos.ca/twitcher/ows/proxy/flyingpigeon/wps"


@pytest.fixture(scope="module")
def wps():
    return WPSClient(url=URL_EMU)


@pytest.fixture(scope="module")
def wps_offline():
    return WPSClient(url=URL_EMU, caps_xml=EMU_CAPS_XML, desc_xml=EMU_DESC_XML)


@pytest.fixture(scope="module")
def process():
    """Return an owslib.Process instance taken from Finch.subset_gridpoint."""
    reader = owslib.wps.WPSDescribeProcessReader()
    root = reader.readFromString(open(resource_file("process_description.xml")).read())
    xml = root.findall("ProcessDescription")[0]
    return owslib.wps.Process(xml)


def test_emu_offline(wps_offline):
    assert "Hello" in wps_offline.hello.__doc__


def test_wps_supported_languages(wps_offline):
    assert wps_offline.languages.supported == ["en-US", "fr-CA"]


@pytest.mark.online
def test_wps_with_language_arg():
    wps = WPSClient(URL_EMU, language="fr-CA")
    assert wps.language == "fr-CA"
    p = wps._processes["translation"]
    assert p.title == "Processus traduit"
    resp = wps.translation(10)
    assert resp.processOutputs[0].title == "Sortie #1"


@pytest.mark.online
@pytest.mark.xfail(reason="a wps process has invalid defaultValue Inf")
def test_52north():
    """This WPS server has process and input ids with dots and dashes."""
    WPSClient(url_52n)


@pytest.mark.online
def test_52north_simple():
    """Check only a few 52north processes."""
    WPSClient(
        url_52n,
        processes=[
            "org.n52.wps.server.algorithm.r.AnnotationValidation",
            "org.n52.wps.server.r.uncertweb.make-realizations",
        ],
    )


def test_52north_offline():
    """Check offline 52north processes."""
    WPSClient(
        url_52n,
        caps_xml=open(resource_file("wps_52n_caps.xml"), "rb").read(),
        desc_xml=open(resource_file("wps_52n_desc.xml"), "rb").read(),
    )


@pytest.mark.online
def test_flyingpigeon():
    WPSClient(url_fly)


def test_flyingpigeon_offline():
    WPSClient(
        url_fly,
        caps_xml=open(resource_file("wps_fly_caps.xml"), "rb").read(),
        desc_xml=open(resource_file("wps_fly_desc.xml"), "rb").read(),
    )


@pytest.mark.online
def test_wps_client_backward_compability():
    from birdy import BirdyClient

    BirdyClient(url=URL_EMU)
    from birdy import import_wps

    import_wps(url=URL_EMU)


def test_wps_docs(wps_offline):
    assert "Processes" in wps_offline.__doc__


@pytest.mark.online
def test_wps_client_single_output(wps):
    result = wps.hello("david")
    assert result.get()[0] == "Hello david"
    result = wps.binaryoperatorfornumbers(inputa=1, inputb=2, operator="add")
    assert result.get()[0] == 3.0


def test_wps_nb_form(wps_offline):
    for pid in list(wps_offline._processes.keys()):
        if pid in [
            "bbox",
        ]:  # Unsupported
            continue
        nb_form(wps_offline, pid)


@pytest.mark.online
def test_wps_client_dummy_process(wps):
    # For multiple outputs, the output is a namedtuple
    result = wps.dummyprocess(10, 20)
    output = result.get()
    assert output[0] == "11"
    assert output[1] == "19"
    assert output.output1 == "11"
    assert output.output2 == "19"


@pytest.mark.online
def test_wps_wordcounter(wps):
    fn = "/tmp/text.txt"
    with open(fn, "w") as f:
        f.write("Just an example")
    out = wps.wordcounter(text=fn).get(asobj=True)
    assert len(out.output) == 3


@pytest.mark.online
def test_interactive(capsys):
    m = WPSClient(url=URL_EMU, progress=True)
    assert m.hello("david").get()[0] == "Hello david"
    captured = capsys.readouterr()
    assert captured.out.startswith(str(datetime.date.today()))
    assert m.binaryoperatorfornumbers().get()[0] == 5


@pytest.mark.online
def test_wps_client_multiple_outputs(wps):
    pytest.importorskip("metalink.download")
    resp = wps.multiple_outputs(2)

    # As reference
    [meta, meta4] = resp.get()
    assert meta.startswith("http")
    assert meta.endswith(".metalink")

    assert meta4.startswith("http")
    assert meta4.endswith(".meta4")

    # As objects
    [files, files4] = resp.get(asobj=True)
    print(files)
    assert len(files) == 2
    assert len(files4) == 2


@pytest.mark.online
def test_process_subset_only_one():
    m = WPSClient(url=URL_EMU, processes=["nap", "sleep"])
    assert count_class_methods(m) == 2

    m = WPSClient(url=URL_EMU, processes="nap")
    assert count_class_methods(m) == 1


@pytest.mark.online
def test_process_subset_names():
    with pytest.raises(ValueError, match="missing"):
        WPSClient(url=URL_EMU, processes=["missing"])
    with pytest.raises(ValueError, match="wrong, process, names"):
        WPSClient(url=URL_EMU, processes=["wrong", "process", "names"])


@pytest.mark.online
def test_asobj(wps):
    resp = wps.ncmeta(dataset=resource_file("dummy.nc"))
    out = resp.get(asobj=True)
    assert "URL" in out.output  # Part of expected text file content.

    resp = wps.ncmeta(dataset="file://" + resource_file("dummy.nc"))
    out = resp.get(asobj=True)
    assert "URL" in out.output

    with open(resource_file("dummy.nc"), "rb") as fp:
        resp = wps.ncmeta(dataset=fp)
        out = resp.get(asobj=True)
        assert "URL" in out.output

    # If the converter is missing, we should still get the data as bytes.
    resp._converters = []
    out = resp.get(asobj=True)
    assert isinstance(out.output, bytes)


@pytest.mark.online
def test_asobj_non_pythonic_id(wps):
    import json

    d = {"a": 1}
    resp = wps.non_py_id(input_1=1, input_2=json.dumps(d))
    out = resp.get(asobj=True)
    assert out.output_1 == 2
    assert out.output_2 == d


@pytest.mark.skip
def test_esgfapi(wps):
    from owslib_esgfwps import Domain, Dimension, Variable

    uri = resource_file("test.nc")

    variable = Variable(var_name="meantemp", uri=uri, name="test")
    domain = Domain([Dimension("time", 0, 10, crs="indices")])

    resp = wps.emu_subset(variable=variable, domain=domain)
    out = resp.get(asobj=True)
    assert "netcdf" in out.ncdump


@pytest.mark.online
def test_inputs(wps):
    import netCDF4 as nc

    time_ = datetime.datetime.now().time()
    date_ = datetime.datetime.now().date()
    datetime_ = datetime.datetime.now()
    result = wps.inout(
        string="test string",
        int=3,
        float=(3.5, 1.0),
        boolean=True,
        angle=67.0,
        time=time_.isoformat(),
        date=date_.isoformat(),
        datetime=datetime_.isoformat(sep=" "),
        string_choice="rock",
        string_multiple_choice="sitting duck",
        int_range=5,
        any_value="7",
        ref_value="Scots",
        text="some unsafe text &<",
        dataset="file://" + resource_file("dummy.nc"),
    )
    expected = (
        "test string",
        3,
        4.5,
        True,
        67.0,
        time_,
        date_,
        datetime_,
        "rock",
        "sitting duck",
        5,
        "7",
        "Scots",
        "some unsafe text &<",
    )
    assert expected == result.get(asobj=True)[:-2]

    expected_netcdf = nc.Dataset(resource_file("dummy.nc"))
    netcdf = result.get(asobj=True)[-2]
    assert list(expected_netcdf.variables) == list(netcdf.variables)
    assert expected_netcdf.title == netcdf.title

    # bbox = result[-1]
    # assert bbox.crs == crs.Crs("epsg:4326")
    # assert bbox.dimensions == 2


@pytest.mark.online
def test_netcdf():
    import netCDF4 as nc
    from birdy.client.converters import Netcdf4Converter, JSONConverter

    # Xarray is the default converter. Use netCDF4 here.
    if nc.getlibversion() > "4.5":
        m = WPSClient(
            url=URL_EMU,
            processes=["output_formats"],
            converters=[Netcdf4Converter, JSONConverter],
        )
        ncdata, jsondata = m.output_formats().get(asobj=True)
        assert isinstance(ncdata, nc.Dataset)
        ncdata.close()
        assert isinstance(jsondata, dict)


@pytest.mark.online
def test_xarray_converter(wps):
    pytest.importorskip("xarray")
    import xarray as xr

    ncdata, jsondata = wps.output_formats().get(asobj=True)
    assert isinstance(ncdata, xr.Dataset)


def test_sort_inputs(process):
    # The first three inputs are all minOccurs=1 with no default, so we expect them to remain in the same order.
    ps = sorted(process.dataInputs, key=sort_inputs_key)
    for i in range(3):
        assert ps[i] == process.dataInputs[i]


def test_sort_inputs_conditions():
    """
    The order should be:
     - Inputs that have minOccurs >= 1 and no default value
     - Inputs that have minOccurs >= 1 and a default value
     - Every other input
    """

    i = mock.Mock()
    i.minOccurs = 1
    i.defaultValue = None
    assert sort_inputs_key(i) == [False, False, True]

    i = mock.Mock()
    i.minOccurs = 1
    i.defaultValue = "default"
    assert sort_inputs_key(i) == [True, False, True]

    i = mock.Mock()
    i.minOccurs = 0
    assert sort_inputs_key(i) == [True, True, False]

    i = mock.Mock()
    i.minOccurs = 0
    i.defaultValue = "default"
    assert sort_inputs_key(i) == [True, True, False]


def test_all_subclasses():
    c = converters.all_subclasses(converters.BaseConverter)
    assert converters.Meta4Converter in c


def count_class_methods(class_):
    import types

    return len(
        [
            f
            for f in list(class_.__dict__.values())
            if isinstance(f, types.MethodType) and not f.__name__.startswith("_")
        ]
    )


def test_jsonconverter():
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


def test_zipconverter():
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

    [oa, ob] = converters.convert(f, path="/tmp")
    assert oa == {"a": 1}
    assert len(ob.splitlines()) == 2


def test_jpeg_imageconverter():
    "Since the format is not supported, bytes will be returned."
    fn = tempfile.mktemp(suffix=".jpeg")
    with open(fn, "w") as f:
        f.write(
            "jpeg.jpg JPEG 1x1 1x1+0+0 8-bit Grayscale Gray 256c 107B 0.000u 0:00.000"
        )

    b = converters.convert(fn, path="/tmp")
    assert isinstance(b, bytes)


class TestIsEmbedded:
    remote = "http://remote.org"
    local = "http://localhost:5000"
    fn = resource_file("dummy.nc")
    path = Path(resource_file("dummy.nc"))
    uri = "file://" + fn
    url = "http://some.random.site/test.txt"

    def test_string(self):
        assert is_embedded_in_request(self.remote, "just a string")
        assert is_embedded_in_request(self.local, "just a string")

    def test_file_like(self):
        import io

        f = io.StringIO()
        f.write("just a string")
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
