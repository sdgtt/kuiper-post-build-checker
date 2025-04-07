import pytest
import utils

@pytest.mark.skipif(
    not pytest.config.getoption("-m") == "kuiper",
    reason="Skipping because the 'kuiper' marker is not passed"
)
@pytest.mark.kuiper
@pytest.mark.parametrize("name", utils.get_packages())
def test_packages(host, name):
    pkg = host.package(name)
    assert pkg.is_installed