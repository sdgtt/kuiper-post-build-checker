import pytest
import re
import time
import utils

import functools

@pytest.fixture
def target_info():
    _target_info = None
    target = utils.get_value_from_config('devices', 'target')
    c = target.get('carrier')
    d = target.get('daughter')
    if c and d:
        _target_info = utils.get_device_info(c, d)
    return _target_info

@pytest.fixture
def target():
    target = utils.get_value_from_config('devices', 'target')
    return target

@utils.timeout()
def test_dmesg_error(host):
    command = 'dmesg | grep error'
    out = host.run(command)
    assert out.rc == 1
    assert not out.stdout
    assert not out.stderr

@utils.timeout()
def test_dmesg_sysid(host, target):

    def is_carrier_match(data, key):
        return data.find('[' + key + ']') != -1

    def is_daughter_match(data, key):
        return data.find('[' + key + ']') != -1

    def is_git_clean(data):
        return data.find('clean') != -1

    command = 'dmesg | grep sysid'
    out = host.run(command)
    assert out.rc == 0
    assert not out.stderr
    assert is_carrier_match(out.stdout, target.get('carrier'))
    assert is_daughter_match(out.stdout, target.get('daughter'))
    assert is_git_clean(out.stdout)

@utils.timeout()
def test_iio_info_device(host, target_info):
    assert target_info
    command = 'iio_info | grep iio:device'
    out = host.run(command)
    for target in target_info.get('iio_devices'):
        assert target in out.stdout

@utils.timeout()
@pytest.mark.parametrize("lib", utils.get_built_libs())
def test_libs(host, lib):
    command = '/usr/sbin/ldconfig -v 2> /dev/null | grep {}'.format(lib)
    out = host.run(command)
    assert out.rc == 0
    assert out.stdout
    assert not out.stderr

@utils.timeout()
@pytest.mark.parametrize("command", utils.get_commands())
def test_commands(host, command):
    out = host.exists(command)
    assert out
