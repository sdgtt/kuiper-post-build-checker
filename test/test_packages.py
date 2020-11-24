import pytest
from sqa_post_boot_checker import utils

@pytest.mark.parametrize("name", utils.get_packages())
@pytest.mark.parametrize("host", utils.get_host())
def test_packages(host, name):
    pkg = host.package(name)
    assert pkg.is_installed