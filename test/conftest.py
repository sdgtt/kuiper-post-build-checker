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

    parser.addoption(
        "--board",
        action="store",
        default=None,
        help="Common project name of the board. ex: socfpga_arria10_socdk_daq2"
    )
    
    parser.addoption(
        "--kuiper",
        action="store_true",
        help="Run tests related to Kuiper such as packages and shell commands",
    )

def pytest_runtest_setup(item):
    target = item.config.getoption("artifactory_target")
    if target and not item.get_closest_marker("artifactory_check"):
        pytest.skip("Skipping non-artifactory_check test because --artifactory-target is used")

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

@pytest.fixture
def project_name(request):
    # if host is given, ip and config will be ignored
    # if ip is given, will default to paramiko backend and config will be ignore
    # if host and ip is not given, config will be used
    return request.config.getoption("--board")