import pytest
from birdy import native_client


def test_BirdyMod():
    m = native_client(url="http://localhost:5000/wps")
    assert m.hello('david') == 'Hello david'
    assert m.binaryoperatorfornumbers(inputa=1, inputb=2, operator='add') == 3.0
