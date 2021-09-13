from invoke import task
import utils
import os

@task(
    help={
        "tree" : "Checkout to particular tree(branch or commit)"
    },
)
def fetchkuipergen(c, tree=None):
    """ Installs (Clone or pull) copy of ADI Kuiper Gen to host"""
    utils.fetch_files(tree=tree)

@task(iterable=['files'],
    help={
            "files": "Set to test only files specified.",
            "tree" : "Checkout to particular tree(branch or commit)",
            "host" : "Target using format <backend>://<credentials>@<ip>",
            "ip" : "IP of DUT, will assume paramiko backend"
        },
    )
def test(c, files=None, tree=None, host=None, ip=None, hardware_less=True):
    """ Run pytest tests """

    # update adi kuiper gen repo
    utils.fetch_files(tree=tree)

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
        options = options + ' -m "not hardware_check"'


    print('Executing ... python -m pytest -v {} {}'.format(target, options))
    c.run('python -m pytest -v {} {}'.format(target, options))