from subprocess import Popen, PIPE
import os
import numpy as np
from pythonosc import udp_client
import librosa

def mktmp():
    try: os.mkdir('tmp')
    except FileExistsError: pass

def clrtmp():
    try: os.rmdir('tmp')
    except Exception: pass

def get_sv_port():
    """ get the port currently used by the sonic visualizer
    This function will generate tmp files

    return: the port number
    raise: Exception when sonic visualizer is not found on the port list
    """
    mktmp()

    os.system("lsof -c sonic-vi | grep UDP |  sed -e 's/^.*[^0-9]\\([0-9][0-9]*\\) *$/\\1/' | grep -v ' ' | head -1 > tmp/svinfo")
    try:
        with open('tmp/svinfo', 'r') as f:
            port = int(f.readline().strip())

    except Exception:
        raise Exception('Sonic visualizer is probably not running')

    if not np.isnan(port):
        return port

port = get_sv_port()
client = udp_client.SimpleUDPClient('127.0.0.1', port)
print('OSC client up at', port)

def update_client():
    global client
    global port
    new_port = get_sv_port()
    print(port, new_port)
    if port != new_port:
        print('port switched to', new_port)
        port = new_port
        client = udp_client.SimpleUDPClient('127.0.0.1', port)

def send_message(addr, value):
    """Send a osc message to sonic visualizer
    addr -- string        the addr format of a osc package, e.g. '/filter', '/start'
    value -- [string]     as the the value of the osc package

    raise: Exception if the format is not valid or sonic visualizer is broken
    """
    update_client()
    client.send_message(addr, value)

def waveplot(y, sr):
    """send a wave plot to sonic visualizer
    y -- array     the sound samples
    sr -- sample rate
    raise: Exception if the format is not valid or sonic visualizer is broken
    """
    mktmp()
    librosa.output.write_wav('tmp/tmp.wav', y, sr)
    send_message('/open', os.path.abspath('tmp/tmp.wav'))

# TODO: Add functions such as sending bars, music files, etc.
