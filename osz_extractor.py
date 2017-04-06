import os
import sys
import patoolib
import shutil

# This file will extract all .osz files in local directory and delete everything except .mp3 and .osu in them.
# Use letter "N" or "n" as input in terminal to prevent deleting

X = sys.argv[1]
names = os.listdir()
folder_names = [name.replace('.osz', '') for name in names]
folder_names = [name.replace('.', '') for name in folder_names]
n = len(names)

for i in range(n):
    if '.osz' in names[i]:
        os.mkdir(folder_names[i])
        patoolib.extract_archive(names[i], outdir = folder_names[i])
        if X == 'N' or 'n':
            continue
        subnames = os.listdir(folder_names[i])
        for name in subnames:
            path = folder_names[i] + '/' + name
            if '.mp3' not in name and '.osu' not in name:
                if os.path.isdir(path):
                    shutil.rmtree(path)
                else:
                    os.remove(path)
