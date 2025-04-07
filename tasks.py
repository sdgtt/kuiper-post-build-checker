from invoke import task
import utils
import os

@task(
    help={
        "config" : "Configuration file to use",
        "tree" : "Checkout to particular tree(branch or commit)"
    },
)
def fetchkuipergen(c, config=None, tree=None):
    """ Installs (Clone or pull) copy of ADI Kuiper Gen to host"""
    utils.fetch_files(config=config, tree=tree)

@task(iterable=['files'],
    help={
            "config" : "Configuration file to use",
            "files": "Set to test only files specified.",
            "tree" : "Checkout to particular tree(branch or commit)",
            "host" : "Target using format <backend>://<credentials>@<ip>",
            "ip" : "IP of DUT, will assume paramiko backend",
            "hardware_less" : "Run tests without hardware check",
            "artifactory_target" : "Absolute path of target folder containing boot files",
        },
    )
def test(
        c,
        config=None,
        files=None,
        tree=None,
        host=None,
        ip=None,
        hardware_less=True,
        artifactory_target=None
    ):
    """ Run pytest tests """
    # update adi kuiper gen repo
    utils.fetch_files(config=config, tree=tree)

    # build command based on parameters
    target = ''
    options = ''

    for _file in files:
        _file = os.path.join('test', _file)
        print(_file)
        target = target + ' {}'.format(_file)

    if host:
        options = options + ' --host={}'.format(host)
    
    if ip:
        options = options + ' --ip={}'.format(ip)

    if hardware_less:
        options = options + '-m "not hardware_check"'

    if artifactory_target:
        options = options + ' -m "artifactory_check" --artifactory_target={}'\
            .format(artifactory_target)

    cmd = 'python3 -m pytest -vsss {} {}'.format(target, options)

    print(f'Executing {cmd}')
    c.run(cmd)