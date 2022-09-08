import pytest
import utils
import json
import pytest_check as check
import wget
import os
import re
from functools import partial

DESRIPTOR_FILE="/boot/kuiper.json"
# DESRIPTOR_FILE="/boot/projects_descriptor.json"

def get_project_details(pcn):
    '''Returns project details as a function of pcn: project common name.
        ex.: socfpga_arria10_socdk_daq2'''
    common_architectures = [
        ("arria10_", "arria10"),
        ("cyclone5_", "cyclone5"),
        ("zynq-", "zynq"),
        ("zynq-", "zynq"),
        ("zynqmp-", "zynqmp"),
        ("versal-", "versal")
    ]
    common_boards = [
        ("socdk_","socdk"),
        ("de10_nano_","de10nano"),
        ("sockit_","sockit"),
        ("coraz7s-","coraz7s"),
        ("zc702-","zc702"),
        ("zc706-","zc706"),
        ("zed-","zed"),
        ("zcu102-","zcu102"),
        ("adrv9009-zu11eg-","adrv9009zu11eg_adrv2crr"),
        ("vck190-","vck190"),
        ("-bob","ccbob"),
        ("z7035-fmc","ccfmc"),
        ("z7035-packrf","ccpackrf"),
        ("z7020-packrf","ccpackrf"),
    ]
    common_names = [
        ("ad9081$","ad9081"),
        ("adv7511$","adv7511"),
        ("ad9695","ad9695"),
        ("ad9783","ad9783"),
        ("adrv9002$","adrv9002"),
        ("adrv9009","adrv9009"),
        ("adrv9371","adrv9371"),
        ("adrv9375","adrv9375"),
        ("cn0540","cn0540"),
        ("_daq2","daq2"),
        ("fmcdaq2","daq2"),
        ("fmcdaq3","daq3"),
        ("fmcadc2","fmcadc2"),
        ("fmcadc3","fmcadc3"),
        ("fmcjesdadc1","fmcjesdadc1"),
        ("fmcomms11","fmcomms11"),
        ("fmcomms2","fmcomms2"),
        ("fmcomms3","fmcomms3"),
        ("fmcomms4","fmcomms4"),
        ("fmcomms5","fmcomms5"),
        ("fmcomms8","fmcomms8"),
        ("cn0501","cn0501"),
        ("ad4020","ad4020"),
        ("cn0363","cn0363"),
        ("imageon","imageon"),
        ("ad4630-24","ad403x"),
        ("ad7768$","ad7768"),
        ("socdk_fmclidar1","ad_fmclidar1_ebz"),
        ("adv7511-fmclidar1","ad_fmclidar1_ebz"),
        ("rev10-fmclidar1","fmclidar"),
        ("adrv9002_rx2tx2","adrv9002_rx2tx2"),
        ("adrv9002-rx2tx2","adrv9002_rx2tx2"),
        ("cn0506[-_]mii","cn0506_mii"),
        ("cn0506[-_]rgmii","cn0506_rgmii"),
        ("cn0506[-_]rmii","cn0506_rmii"),
        ("ad6676-fmc","ad6676evb"),
        ("ad9265-fmc-125ebz","ad9265_fmc"),
        ("ad9434-fmc","ad9434_fmc"),
        ("ad9739a-fmc","ad9739a_fmc"),
        ("adrv9008-1","adrv9008-1"),
        ("adrv9008-2","adrv9008-2"),
        ("ad9172-fmc-ebz","ad9172_fmc"),
        ("fmcomms5-ext-lo-adf5355","fmcomms5-ext-lo-adf5355"),
        ("z7035-bob-vcmos","adrv9361z7035_cmos"),
        ("z7035-bob-vlvds","adrv9361z7035_lvds"),
        ("z7020-bob-vcmos","adrv9364z7020_cmos"),
        ("z7020-bob-vlvds","adrv9364z7020_lvds"),
        ("z7035-fmc","adrv9361z7035_lvds"),
        ("z7035-packrf","adrv9361z7035_lvds"),
        ("z7020-packrf","adrv9364z7020_lvds"),
        ("ad7768-1-evb","ad77681_evb"),
        ("ad9467-fmc-250ebz","ad9467-fmc"),
        ("otg","adv7511_without_bitstream"),
        ("adrv2crr-fmc-revb","adrv9009zu11eg_adrv2crr"),
        ("multisom-primary","multisom-primary"),
        ("multisom-secondary","multisom-secondary"),
        ("fmcomms8-multisom-primary","fmcomms8_multisom_primary"),
        ("fmcomms8-multisom-secondary","fmcomms8_multisom_secondary"),
        ("xmicrowave","xmicrowave"),
        ("ad9081-vm8-l4","ad9081_m8_l4"),
        ("ad9081-vm4-l8","ad9081_m4_l8"),
        ("ad9081[-_]vnp12","ad9081_np12"),
        ("ad9081-vm8-l4-vcxo122p88","ad9081_m8_l4_vcxo122p88"),
        ("ad9081-v204b-txmode9-rxmode4","ad9081_204b_txmode9_rxmode4"),
        ("ad9081-v204c-txmode0-rxmode1","ad9081_204c_txmode0_rxmode1"),
        ("ad9082-vm4-l8","ad9082_m4_l8"),
        ("ad9083-fmc-ebz","ad9083"),
        ("adrv9008-1","adrv9008-1"),
        ("adrv9008-2","adrv9008-2"),
        ("adrv9002-vcmos","adrv9002_cmos"),
        ("adrv9002-vlvds","adrv9002_lvds"),
        ("adrv9002-rx2tx2-vcmos","adrv9002_rx2tx2_cmos"),
        ("adrv9002-rx2tx2-vlvds","adrv9002_rx2tx2_lvds"),
        ("ad9172-fmc-ebz-mode4","ad9172_mode4"),
    ]

    p_architecture = None
    p_board = None
    p_name = None

    for ar in common_architectures:
        if re.search(ar[0], pcn):
            p_architecture = ar[1]

    for br in common_boards:
        if re.search(br[0], pcn):
            p_board = br[1]

    for pn in common_names:
        if re.search(pn[0], pcn):
            p_name = pn[1]
   
    return (p_architecture, p_board, p_name)

def project_filter(project_dict, filters):
    match = True
    for k,v in filters.items():
        if k in project_dict.keys():
            if not project_dict[k] == v:
                match = False
                break
    return match

def get_boot_files(host, descriptor=DESRIPTOR_FILE, project=None):
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

    # filter project
    if project:
        a,b,n = get_project_details(project)
        assert a
        assert b
        assert n
        filter_dict = dict({
            "architecture": a,
            "board": b,
            "name": n
        })
        projects = filter(partial(project_filter, filters=filter_dict), projects)

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

def test_boot_files(host, project_name):
    fail_flag = False
    bts = get_boot_files(host, DESRIPTOR_FILE, project_name)
    for bt in bts:
        condition = host.file(bt[1]).exists
        message = 'Missing File: Project:{} File:{}'.format(bt[0],bt[1])
        check.is_true(condition, message)
        if condition:
            print(f'Found {bt}')
        else:
            fail_flag = True

    assert not fail_flag

@pytest.mark.artifactory_check
def test_artifactory_boot_files(artifactory_bts):
    assert artifactory_bts
    if artifactory_bts:
        fail_flag = False
        normalized_abts = list()
        descriptor = None
        base_path = os.path.commonpath(artifactory_bts).replace(":/","://")
        print(f"base_path: {base_path} ")
        # find descriptor
        for abt in artifactory_bts:
            nbt = '/boot' + str(abt).replace(str(base_path),'')
            if nbt == DESRIPTOR_FILE:
                descriptor = abt
            normalized_abts.append(nbt)
        bts = get_boot_files(host=None, descriptor=str(descriptor))
        for bt in bts:
            condition = (bt[1] in normalized_abts)
            message = 'Missing File: Project:{} File:{}'.format(bt[0],bt[1])
            check.is_true(condition, message)
            if condition:
                print(f'Found {bt}')
            else:
                fail_flag = True

        assert not fail_flag

