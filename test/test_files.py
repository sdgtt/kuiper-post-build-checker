import pytest
import utils

def test_passwd_file(host):
    passwd = host.file("/etc/passwd")
    assert passwd.contains("root")
    assert passwd.contains("analog")
    assert passwd.user == "root"
    assert passwd.group == "root"
    assert passwd.mode == 0o644

def test_bashrc_file(host):
    passwd = host.file("/home/analog/.bashrc")
    assert passwd.contains("PYTHONPATH")