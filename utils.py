import yaml
import os
import git
import re
import testinfra
import threading
import functools
import pytest
import signal
import shutil
from sys import platform
from artifactory import ArtifactoryPath

FILE_PATH = os.path.dirname(os.path.realpath(__file__))
CONFIG_FILE = 'config.yaml'
PACKAGE_NAME = 'kuiper-post-build-checker'
OS_GEN_REPO_NAME = 'adi-kuiper-gen'
DEFAULT_TIMEOUT_SEC = 60

def timeout(time=DEFAULT_TIMEOUT_SEC):
    ''' 
        A decorator to force target function to timeout gracefully.
        Especially useful in Windows environment when pytest-timeout s
        triggered via signal.alarm does not work.

        If not specified, timeout will be set to DEFAULT_TIMEOUT_SEC
    '''
    def timeout_wrapper(func):
        @functools.wraps(func)
        def inner(*args, **kwargs):

            if platform == "linux" or platform == "linux2":
                signal_interrupt = signal.SIGINT
            elif platform == "win32":
                signal_interrupt = signal.CTRL_C_EVENT

            timer = threading.Timer(time, \
                lambda: os.kill(os.getpid(), signal_interrupt))
            timer.start()
            try:
                res = func(*args, **kwargs)
            except KeyboardInterrupt:
                print('Reached timeout executing {}'.format(func.__name__))
                pytest.fail(msg='Timeout reached for {}'.format(func.__name__))
            finally:
                # if the action ends in specified time, timer is canceled
                timer.cancel()
            return res
        return inner
    return timeout_wrapper

def get_package_path(file_path=None):
    if not file_path:
        file_path = FILE_PATH
    base_path = file_path.split(PACKAGE_NAME)[0]
    return os.path.abspath(os.path.join(base_path, PACKAGE_NAME))

def get_config_file(file_path=None, config=None):
    file_path = file_path if file_path else FILE_PATH
    config_file = config if config else CONFIG_FILE
    config = os.path.join(get_package_path(), config_file)
    return config

def get_value_from_config(*args):
    # read config file
    with open(get_config_file()) as f:
        data = yaml.load(f, Loader=yaml.FullLoader)
        for arg in args:
            if isinstance(data, dict):
                data = data.get(arg)
            else:
                data = None
    return data

def get_path_from_txt(line):
    if not line:
        return
    path = os.path.join(
            get_package_path(),
            '..',
            OS_GEN_REPO_NAME,
            os.path.normpath(line)
        )
    return path

def file_to_list(f, type=None):
    entry_list = []
    if not type:
        file_txt = f.read()
        formatted = re.sub(r"\s", "\n", file_txt)
        for ln in formatted.split("\n"):
            # remove empty lines
            if ln:
                entry_list.append(ln)
    elif type == 'libs':
        libs = re.findall(r'build_([0-9a-zA-Z]+)\s', f.read())
        for i,lib in enumerate(libs):
            if re.search(r'^gr([0-9a-zA-Z]+)', lib):
                libs[i] = re.sub(r'^gr([0-9a-zA-Z]+)',r'libgnuradio-\1',lib)
            elif not re.search(r'^lib([0-9a-zA-Z]+)', lib):
                libs[i] = re.sub(r'^([0-9a-zA-Z]+)',r'lib\1',lib)
        entry_list = libs
    return entry_list

def fetch_files(config=None, tree=None):
    # read config file
    with open(get_config_file(config=config, file_path=None)) as f:
        data = yaml.load(f, Loader=yaml.FullLoader)
        git_uri = data.get("repo").get("uri")
        git_branch = data.get("repo").get("branch")
        git_repo_dir = os.path.join(
            get_package_path(), '..', OS_GEN_REPO_NAME)
    if tree:
        git_branch = tree
    # check if the directory already exists
    if os.path.exists(git_repo_dir):
        print(f"Deleting existing directory: {git_repo_dir}")
        shutil.rmtree(git_repo_dir)
    # always clone the repo to ensure we have the latest version
    print("Cloning from {} to {}".format(git_uri, git_repo_dir))
    git.Repo.clone_from(
        git_uri,
        git_repo_dir,
        branch=git_branch,
        depth=1
    )
    print("Repo {} has been cloned from {} branch {}"\
        .format(git_repo_dir, git_uri, git_branch))

def get_host(backend='paramiko',username='analog', password='analog',host=None, ip=None):
    if host:
        _host = host
    else:
        if ip:
            _host = '{}://{}:{}@{}'.format(backend,username, password, ip)
        else:
            #get hosts from config file
            _host = get_value_from_config('testinfra','host')

    return testinfra.get_host(_host)

def get_services():
    services = []
    # get services from config file
    services = get_value_from_config('services','default')
    return services

def get_packages():
    packages = []
    # read config file
    paths = get_value_from_config('packages','paths')
    for path, val in paths.items():
        if path == 'files':
            for line in val:
                _file_path = get_path_from_txt(line)
                #TODO kimpaller: catch and report test as fail incase file cannot be found.
                with open(_file_path) as f:
                    for _pkg in file_to_list(f):
                        packages.append(_pkg)
    return packages

def get_built_libs():
    libs = []
    libraries = get_value_from_config('libraries')
    for cat, cat_data in libraries.items():
        if cat == 'paths':
            files = cat_data.get('files')
            if isinstance(files,list):
                for line in files:
                    _file_path = get_path_from_txt(line)
                    #TODO kimpaller: catch and report test as fail incase file cannot be found.
                    with open(_file_path) as f:
                        for _lib in file_to_list(f, 'libs'):
                            libs.append(_lib)                    
        if cat =='default':
            if isinstance(cat_data,list):
                for _lib in cat_data:
                    libs.append(_lib)
    return libs

def get_commands():
    commands = []
    _commands = get_value_from_config('commands')
    for cat, cat_data in _commands.items():                 
        if cat =='default':
            if isinstance(cat_data,list):
                for _c in cat_data:
                    commands.append(_c)
    return commands

def get_device_info(carrier, daughter):
    dev = {}
    dev = get_value_from_config(
            'devices', 'profiles',
            carrier, daughter)
    return dev

def check_for_file_only(file):
    special_files = ["zImage", "uImage", "Image"]
    ignored_files = ["bootgen_sysfiles.tgz", "make_parameters.txt"] 
    if '.' in file:
        for i in ignored_files:
            if i in file:
                return False
        return True
    else:
        for i in special_files:
            if i in file:
                return True
    return False

def get_artifactory_boot_files(artifactory_path):
    # path = ArtifactoryPath("https://<artifactory_server>/<path to parent folder>")
    if re.search(r'20[12]\d_[0-3]\d_[0-3]\d-\d{2}_\d{2}_\d{2}', artifactory_path):
        latest_path = ArtifactoryPath(artifactory_path)
    else:
        path = ArtifactoryPath(artifactory_path)
        builds = [ p for p in path.glob("*")]
        latest_path = ArtifactoryPath(builds[-1])
    latest_path_files = list()
    for f in latest_path.rglob("*"):
        if check_for_file_only(f.name):
            latest_path_files.append(f)
            print(f"Detected {f}")
    return  latest_path_files
