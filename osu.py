import numpy as np
from parse import parse

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

    def read_next(self):
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
    def is_slider(type_info):
        return type_info & HitObjectType.Slider > 0

    def read(self):
        pos_x = self.read_next()
        pos_y = self.read_next()
        start_time = self.read_next()
        type_and_combo_offset = self.read_next()
        sound_type = self.read_next()

        obj = {'x': pos_x, 'y': pos_y, 'time': start_time, 'type': type_and_combo_offset, 'sound': sound_type}

        if self.is_slider(type_and_combo_offset):
            curve = self.read_next()
            curve_type = curve[0]
            curve_points = curve[1:]

            segment_count = self.read_next()
            spatial_length = self.read_next()

            extra_fields = ['sount_type_list', 'sample_set_list', 'slider_extra', 'sample_addition']
            extra_values = {}
            for field in extra_fields:
                extra_values[field] = self.read_next()

            additional_fields = {'curve_type': curve_type, 'curve': curve_points,
                                 'segment_count': segment_count, 'spatial_length': spatial_length}

            for key, value in additional_fields.items():
                obj[key] = value

        return obj


def load_hit_objects(filename):
    """read hit objects from osu file
    filename - string       the file name of a .osu file
    raise - All kinds of exceptions if the file is not well formatted
    """
    if '.osu' not in filename:
        print('Warning: file does not appear to be a osu file.')
    with open(filename, 'r') as f:
        for line in f:
            if f.readline().strip() == '[HitObjects]': break
        hit_objects = []
        for line in f:
            if line.strip() == '': continue
            hit_objects.append(OSUHitObjectReader(line).read())

    return hit_objects

