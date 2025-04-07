import pytest
import utils

@pytest.mark.parametrize("name", utils.get_services())
def test_services(host, name):
    service = host.service(name)
    assert service.is_running