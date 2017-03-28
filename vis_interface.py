from subprocess import Popen, PIPE
import os
import numpy as np
from pythonosc import udp_client

def get_sv_port():
    """ get the port currently used by the sonic visualizer
    This function will generate tmp files

    return: the port number
    raise: Exception when sonic visualizer is not found on the port list
    """

    try: os.mkdir('tmp')
    except FileExistsError: pass
    os.system("lsof -c sonic-vi | grep UDP |  sed -e 's/^.*[^0-9]\\([0-9][0-9]*\\) *$/\\1/' | grep -v ' ' | head -1 > tmp/svinfo")
    try:
        with open('tmp/svinfo', 'r') as f:
            port = int(f.readline().strip())

    except Exception:
        raise Exception('Sonic visualizer is probably not running')

    if not np.isnan(port):
        return port

client = udp_client.SimpleUDPClient('127.0.0.1', get_sv_port())

def send_message(addr, value):
    """Send a osc message to sonic visualizer
    addr -- string        the addr format of a osc package, e.g. '/filter', '/start'
    value -- [string]     as the the value of the osc package

    raise: Exception if the format is not valid or sonic visualizer is broken
    """
    client.send_message(addr, value)

# TODO: Add functions such as sending bars, music files, etc.
