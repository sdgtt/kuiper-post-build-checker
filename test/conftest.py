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

    parser.addoption(
        "--artifactory_target",
        action="store",
        default=None,
        help="Absolute path of target folder containing boot files"
    )
    
@pytest.fixture
def host(request):
    # if host is given, ip and config will be ignored
    # if ip is given, will default to paramiko backend and config will be ignore
    # if host and ip is not given, config will be used
    host = request.config.getoption("--host")
    ip = request.config.getoption("--ip")
    return utils.get_host(host=host,ip=ip)

@pytest.fixture
def artifactory_bts(request):
    # artifactory_target = "https://artifactory.analog.com/artifactory/sdg-generic-development/boot_partition/master"
    artifactory_target = request.config.getoption("--artifactory_target")
    if artifactory_target:
        return utils.get_artifactory_boot_files(artifactory_path=artifactory_target)

    return None
