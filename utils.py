import yaml
import os
import git
import re
import testinfra
import threading
import functools
import pytest
import signal
from sys import platform

FILE_PATH = os.path.dirname(os.path.realpath(__file__))
CONFIG_FILE = 'config.yaml'
PACKAGE_NAME = 'sqa_post_boot_checker'
OS_GEN_REPO_NAME = 'adi-kuiper-gen'
DEFAULT_TIMEOUT_SEC = 60

def timeout(func):
    ''' 
        A decorator to force target function to timeout gracefully.
        Especially useful in Windows environment when pytest-timeout s
        triggered via signal.alarm does not work.

        Modify DEFAULT_TIMEOUT_SEC to desired timeout in seconds.
    '''
    @functools.wraps(func)
    def inner(*args, **kwargs):

        if platform == "linux" or platform == "linux2":
            signal_interrupt = signal.SIGINT
        elif platform == "win32":
            signal_interrupt = signal.CTRL_C_EVENT

        timer = threading.Timer(DEFAULT_TIMEOUT_SEC, \
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

    try:
        # use existing repo and update for any changes from remote using pull
        print("Updating repo {}".format(git_repo_dir))
        g = git.Repo(git_repo_dir).git
        if not tree:
            tree = g.log(pretty="format:%H",n=1)
        g.checkout(tree)
        print("Checkout to {}".format(tree))   
        status = g.pull('origin',tree)
        print("Repo {} status: {}".format(git_repo_dir, status))
    except(git.exc.NoSuchPathError, git.exc.InvalidGitRepositoryError) as exc:
        # create a new repo by cloning remote
        print(str(exc))
        print("Cloning from {} to {}".format(git_uri, git_repo_dir))
        g = git.Git(os.path.join(get_package_path(), '..'))
        g.clone(git_uri)
        print("Repo {} has been cloned from {} branch {}"\
            .format(git_repo_dir, git_uri, git_branch))
        if tree:
            g = git.Repo(git_repo_dir).git
            status = g.checkout(tree)
            print("Checkout to {}".format(tree))

def get_host():
    hosts = []
    #get hosts from config file
    _hosts = get_value_from_config('testinfra','hosts')
    for _host in _hosts:
        host = testinfra.get_host(_host)
        hosts.append(host)
    return hosts

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
    # read config file
    paths = get_value_from_config('libraries','paths')
    for path, val in paths.items():
        if path == 'files':
            for line in val:
                _file_path = get_path_from_txt(line)
                #TODO kimpaller: catch and report test as fail incase file cannot be found.
                with open(_file_path) as f:
                    for _lib in file_to_list(f, 'libs'):
                        libs.append(_lib)
    return libs

def get_device_info(carrier, daughter):
    dev = {}
    dev = get_value_from_config(
            'devices', 'profiles',
            carrier, daughter)
    return dev