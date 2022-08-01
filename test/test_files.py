import pytest
import utils
import json
import pytest_check as check
import wget
import os

DESRIPTOR_FILE="/boot/kuiper.json"
# DESRIPTOR_FILE="/boot/projects_descriptor.json"

def get_boot_files(host, descriptor=DESRIPTOR_FILE):
    ''' Returns a list of files defined on the descriptor file '''
    descriptor_dict = dict()
    boot_files = list()
    if host:    
        project_descriptor = host.file(descriptor)
        assert project_descriptor.exists
        if project_descriptor.exists:
            cmd = host.run("cat {}".format(descriptor))
            assert cmd.rc == 0
            descriptor_dict = json.loads(cmd.stdout)
    else:
        # files are from artifactory
        #dl descriptor
        filename = wget.download(descriptor)
        with open(filename, 'r') as f:
            descriptor_dict = json.loads(f.read())

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
        if condition:
            print(f'{bt} found')
        message = 'Missing File: Project:{} File:{}'.format(bt[0],bt[1])
        check.is_true(condition, message)

def test_artifactory_boot_files(artifactory_bts):
    if artifactory_bts:
        normalized_abts = list()
        descriptor = None
        base_path = os.path.commonpath(artifactory_bts).replace(":/","://")
        print(base_path)
        # find descriptor
        for abt in artifactory_bts:
            nbt = '/boot' + str(abt).replace(str(base_path),'')
            print(nbt)
            if nbt == DESRIPTOR_FILE:
                descriptor = abt
            normalized_abts.append(nbt)
        print(descriptor)
        bts = get_boot_files(host=None, descriptor=str(descriptor))
        print(bts)
        for bt in bts:
            condition = (bt in normalized_abts)
            message = 'Missing File: Project:{} File:{}'.format(bt[0],bt[1])
            check.is_true(condition, message)
    else:
        print("Empty artifactory_bts")

