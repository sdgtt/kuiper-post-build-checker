import pytest
import utils
import json
import pytest_check as check

DESRIPTOR_FILE="/boot/kuiper.json"
# DESRIPTOR_FILE="/boot/projects_descriptor.json"

def get_boot_files(host, descriptor=DESRIPTOR_FILE):
    boot_files = []    
    project_descriptor = host.file(descriptor)
    assert project_descriptor.exists
    if project_descriptor.exists:
        cmd = host.run("cat {}".format(descriptor))
        assert cmd.rc == 0
        if cmd.rc == 0:
            descriptor_dict = json.loads(cmd.stdout)
            projects = descriptor_dict['projects']
            for project in projects:
                # if not project['kernel'] in [ bt[1] for bt in boot_files]:
                    # boot_files.append((project['name'],project['kernel']))
                boot_files.append((project['name'],project['kernel']))
                if "preloader" in project:
                    boot_files.append((project['name'],project['preloader']))
                files = project['files']
                for f in files:
                    boot_files.append((project['name'],f['path']))
    return boot_files

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

def test_boot_files(host):
    bts = get_boot_files(host)
    for bt in bts:
        condition = host.file(bt[1]).exists
        message = 'Missing File: Project:{} File:{}'.format(bt[0],bt[1])
        check.is_true(condition, message)