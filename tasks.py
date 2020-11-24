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
            "tree" : "Checkout to particular tree(branch or commit)"
        },
    )
def test(c, files=None, tree=None):
    """ Run pytest tests """

    # update adi kuiper gen repo
    utils.fetch_files(tree=tree)

    # build command based on parameters
    target = ''
    for _file in files:
        _file = os.path.join('test', _file)
        print(_file)
        target = target + ' {}'.format(_file)
    print('Executing ... python -m pytest -v {}'.format(target))
    c.run('python -m pytest -v {}'.format(target))