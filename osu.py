import numpy as np
from parse import parse
import librosa
import sys

class HitObjectType:
    Normal = 1
    Slider = 2
    NewCombo = 4
    NormalNewCombo = 5
    SliderNewCombo = 6
    Spinner = 8
    ColourHax = 112
    Hold = 128
    ManiaLong = 128


class OSUHitObjectReader:

    def __init__(self, hit_object_string):
        self.hit_object_string = hit_object_string.strip()

    def _read_next(self):
        comma_pos = self.hit_object_string.find(',')
        if comma_pos < 0:
            segment = self.hit_object_string
            self.hit_object_string = ''
        else:
            segment = self.hit_object_string[:comma_pos]
            self.hit_object_string = self.hit_object_string[comma_pos+1:]

        if segment == '':
            return None

        # process this segment
        if ':' not in segment and '|' not in segment:
            try:
                return int(segment)
            except ValueError:
                return float(segment)

        if ':' in segment and '|' not in segment:
            return [int(v) for v in segment.split(':') if v != '']

        segments = segment.split('|')
        value_list = []
        for seg in segments:
            if len(seg) == 1 and seg.isalpha():
                value_list.append(seg)
            elif ':' not in seg:
                value_list.append(int(seg))
            else:
                value_list.append([int(v) for v in seg.split(':') if v != ''])
        return value_list

    @staticmethod
    def _is_slider(type_info):
        return type_info & HitObjectType.Slider > 0

    def read(self):
        pos_x = self._read_next()
        pos_y = self._read_next()
        start_time = self._read_next()
        type_and_combo_offset = self._read_next()
        sound_type = self._read_next()

        obj = {'x': pos_x, 'y': pos_y, 'time': start_time, 'type': type_and_combo_offset, 'sound': sound_type}

        if self._is_slider(type_and_combo_offset):
            curve = self._read_next()
            curve_type = curve[0]
            curve_points = curve[1:]

            segment_count = self._read_next()
            spatial_length = self._read_next()

            extra_fields = ['sount_type_list', 'sample_set_list', 'slider_extra', 'sample_addition']
            extra_values = {}
            for field in extra_fields:
                extra_values[field] = self._read_next()

            additional_fields = {'curve_type': curve_type, 'curve': curve_points,
                                 'segment_count': segment_count, 'spatial_length': spatial_length}

            for key, value in additional_fields.items():
                obj[key] = value

        return obj


class OSUData:

    def __init__(self, sr=22050):
        self.sr = sr
        self.hit_objects = None
        self.music = None

    def _guard_osu(self):
        if self.hit_objects is None:
            raise Exception('not initialized with osu file')

    def _guard_music(self):
        if self.music is None:
            raise Exception('not initialized with music file')


    def read_osu(self, filename):
        if '.osu' not in filename:
            sys.stderr.write('Warning: file {} is not a .osu file'.format(filename))
        with open(filename, 'r') as f:

            # move file cursor to the start of hit objects
            for line in f:
                if f.readline().strip() == '[HitObjects]':
                    break

            self.hit_objects = []
            for line in f:

                # skip empty lines
                if line.strip() == '': continue
                self.hit_objects.append(OSUHitObjectReader(line).read())
        return self

    def read_music(self, filename):
        self.music, self.sr = librosa.load(filename, self.sr)
        return self

    def encode_basic(self):
        "Encodes the hit objects to only contain time, x, y features"
        self._guard_osu()
        self._guard_music()
        return np.array([[int(obj['time'] / 1000 * self.sr), obj['x'], obj['y']] for obj in self.hit_objects]), self.music

    def encode_stft_seq(self, n_fft=2048, hop_length=64):
        """
        Encode the osu file to [(hit, x, y)] where
        hit=0,1 indicates whether there is a cake,
        x,y indicate the position of the cake

        Encode the music file to the frequency domain with stft(n_fft, hop_length)
        """
        samples, music = self.encode_basic()
        stft = np.abs(librosa.stft(self.music, n_fft, hop_length)).T
        frames = librosa.samples_to_frames(samples[:, 0], hop_length, n_fft)
        seq = np.zeros([len(stft), 3])
        for frame, sample in zip(frames, samples):
            seq[frame] = 1, sample[1], sample[2]
        return seq, stft

    def encode_stft_one_hot(self, n_fft=2048, hop_length=64):
        """
        Extract the hits and ignore coordinates, then one-hot the hits
        """
        seq, stft = self.encode_stft_seq()
        return np.array([[int(h==0), int(h==1)] for h,_,_ in seq]), stft

    def encode_basic_seq(self):
        "Encodes the hit objects using basic encoding and convert to sequance"
        self._guard_osu()
        self._guard_music()
        samples, music = self.encode_basic()
        seq = np.zeros([len(music), 3])
        for sample in samples:
            seq[sample[0]] = 1, sample[1], sample[2]
        return seq, music


data = OSUData().read_osu('./sample.osu').read_music('./sample.wav')
