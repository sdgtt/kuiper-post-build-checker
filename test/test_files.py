import pytest
from sqa_post_boot_checker import utils

@pytest.mark.parametrize("host", utils.get_host())
def test_passwd_file(host):
    passwd = host.file("/etc/passwd")
    assert passwd.contains("root")
    assert passwd.contains("analog")
    assert passwd.user == "root"
    assert passwd.group == "root"
    assert passwd.mode == 0o644

@pytest.mark.parametrize("host", utils.get_host())
def test_bashrc_file(host):
    passwd = host.file("/home/analog/.bashrc")
    assert passwd.contains("PYTHONPATH")