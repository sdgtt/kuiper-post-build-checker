import yaml
from nebula import network
import os
import glob
import re

import pytest

def read_log(board_name):
    pattern = os.getcwd() + '/'+ board_name +'_*.log'
    lines = list()
    for file_path in glob.glob(pattern):
        try:
            with open(file_path, 'r') as file:
                lines = file.readlines()
        except Exception as e:
            print(f"Error occurred: {e}")
    return lines

#########################################
@pytest.mark.parametrize("board", board)
@pytest.mark.parametrize("configFile", yamlFile)
def test_free_memory(board):

    n = network(yamlfilename=configFile, board_name=board)
    n.run_ssh_command(command="dmesg | grep -iE 'sysid|mem' ; free")
    
    log = read_log(board)

    sha = ''
    mem = {}
    swap = {}
    keys = ['total', 'used', 'free', 'shared', 'buff/cache', 'available']
    memory_type = ['Mem:', 'Swap:']

    for line in log:
        if 'git' in line:
            matches = re.findall(r'<(.*?)>', line)
            sha =  ' '.join(matches)
        for memory in memory_type:
            tmp_dict = memory.lower()[:-1]
            if memory in line:
                values = line.split()[1:]
                for index, value in enumerate(values):
                    eval(tmp_dict)[keys[index]] = int(value)

    assert mem['free'] > 0.05 * mem['total']
    if board != 'pluto':
        assert swap['free'] > 0.05 * swap['total']