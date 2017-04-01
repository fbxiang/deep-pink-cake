from subprocess import Popen, PIPE
import os
import numpy as np
from pythonosc import udp_client
import librosa


def get_sv_port():
    """ get the port currently used by the sonic visualizer
    This function will generate tmp files

    return: the port number
    raise: Exception when sonic visualizer is not found on the port list
    """

    os.system("lsof -c sonic-vi | grep UDP |  sed -e 's/^.*[^0-9]\\([0-9][0-9]*\\) *$/\\1/' | grep -v ' ' | head -1 > /tmp/svinfo")
    try:
        with open('/tmp/svinfo', 'r') as f:
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
    librosa.output.write_wav('tmp/tmp.wav', y, sr, True)
    send_message('/open', '/tmp/tmp.wav')


def spectrogram(y, sr):
    """send a spectrogram to sonic visualizer
    y -- array     the sound samples
    sr -- sample rate
    raise: Exception if the format is not valid or sonic visualizer is broken
    """
    librosa.output.write_wav('tmp/tmp.wav', y, sr, True)
    send_message('/open', '/tmp/tmp.wav')
    send_message('/add', ['spectrogram'])


def export_labels(label_times, filename='/tmp/labels.txt'):
    """export a sv readable label file
    label_times -- number array      the time points
    filename -- string               file name to save the label file
    raise: Assertion Error if the array are not numbers
           Some other exception is file is invalid
    """
    for t in label_times:
        assert(t is int or t is float)
    with open(filename, 'w') as f:
        for t in label_times:
            f.write('{}\tNew Point\n'.format(t))
