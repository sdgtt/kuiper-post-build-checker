import pytest
import utils

@pytest.mark.parametrize("name", utils.get_services())
@pytest.mark.parametrize("host", utils.get_host())
def test_services(host, name):
    service = host.service(name)
    assert service.is_running