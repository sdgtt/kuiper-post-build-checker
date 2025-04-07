import pytest
import utils

@pytest.mark.skipif(
    not pytest.config.getoption("-m") == "kuiper",
    reason="Skipping because the 'kuiper' marker is not passed"
)
@pytest.mark.kuiper
@pytest.mark.parametrize("name", utils.get_services())
def test_services(host, name):
    service = host.service(name)
    assert service.is_running