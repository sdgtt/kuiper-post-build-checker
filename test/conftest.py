import pytest
import utils

def pytest_addoption(parser):
    parser.addoption(
        "--ip",
        action="store",
        default=None,
        help="IP of DUT"
    )

    parser.addoption(
        "--host",
        action="store",
        default=None,
        help="complete backend format of target i.e. <backend>://<credentials>@<ip>"
    )
    
@pytest.fixture
def host(request):
    # if host is given, ip and config will be ignored
    # if ip is given, will default to paramiko backend and config will be ignore
    # if host and ip is not given, config will be used
    host = request.config.getoption("--host")
    ip = request.config.getoption("--ip")
    return utils.get_host(host=host,ip=ip)
