import pytest
import re
import time
import utils

@pytest.mark.parametrize("name", utils.get_devices())
def test_device(host, name):
    device_path = "/dev/" + name
    print(device_path)
    assert host.file(device_path).exists
