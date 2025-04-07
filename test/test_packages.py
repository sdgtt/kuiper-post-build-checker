import pytest
import utils

@pytest.mark.kuiper
@pytest.mark.parametrize("name", utils.get_packages())
def test_packages(host, name):
    pkg = host.package(name)
    assert pkg.is_installed