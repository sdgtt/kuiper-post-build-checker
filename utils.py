import yaml
import os
import git
import re
import testinfra

FILE_PATH = os.path.dirname(os.path.realpath(__file__))
CONFIG_FILE = 'config.yaml'
PACKAGE_NAME = 'sqa_post_boot_checker'
OS_GEN_REPO_NAME = 'adi-kuiper-gen'

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
            print(arg)
            data = data.get(arg)
    print(data)
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

def file_to_list(f):
    entry_list = []
    file_txt = f.read()
    formatted = re.sub(r"\s", "\n", file_txt)
    for ln in formatted.split("\n"):
        # remove empty lines
        if ln:
            entry_list.append(ln)
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