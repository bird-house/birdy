import pytest
import json
from birdy import native_client


@pytest.mark.online
def test_birdymod():
    m = native_client(url="http://localhost:5000/wps")
    assert m.hello('david') == 'Hello david'
    assert m.binaryoperatorfornumbers(inputa=1, inputb=2, operator='add') == 3.0
    assert m.dummyprocess(10, 20) == ['11', '19']

    txt, ref = m.multiple_outputs(2)

    assert type(txt) == str
    assert type(ref) == str
    doc = json.loads(ref)
    assert type(doc) == dict
