import os
import sys
import patoolib
import shutil

def file_clear(folder_name):
    """
    This function will clear everything in 'folder_name' except ".mp3" and ".osu" that belongs to
    standard mode (".osu" that belongs to Taiko, CTB or Mania will be deleted)

    @para<str folder_name: the folder needed to be cleared under current working directory>
    """
    subnames = os.listdir(folder_name)

    for name in subnames:
        path = folder_name + '/' + name
        if '.mp3' not in name and '.MP3' not in name and '.osu' not in name:
            if os.path.isdir(path):
                shutil.rmtree(path)
            else:
                os.remove(path)

        elif '.osu' in name:
            indicator = False
            with open(path, 'r', encoding = 'utf-8') as f:
                for line in f:
                    if 'Mode' in line:
                        mode = [int(s) for s in line.split() if s.isdigit()]
                        if mode[0] != 0:
                            indicator = True
                        break
            if indicator == True:
                os.remove(path)

    new_subnames = os.listdir(folder_name)
    if len(new_subnames) == 1:
        new_path = folder_name + '/' + new_subnames[0]
        os.remove(new_path)  
    return

def dir_clear():
    """
    Run 'file_clear()' to every folder in current directory
    """
    names = os.listdir()
    for folder in names:
        if os.path.isdir(folder):
            file_clear(folder)
    return

def extract_osz(if_clear):
    """
    Extract all ".osz" files in current working directory and then clear them or not
    @para<boolean if_clear: run 'dir_clear()' in current working directory if it is "True">
    """
    names = os.listdir()
    folder_names = [name.replace('.osz', '') for name in names]
    folder_names = [name.replace('.', '') for name in folder_names]
    n = len(names)

    for i in range(n):
        if '.osz' in names[i]:
            if os.path.exists(folder_names[i]) == False:
                os.mkdir(folder_names[i])
            patoolib.extract_archive(names[i], outdir = folder_names[i])
    if if_clear == True:
        dir_clear()
        return
    else:
        return

extract_osz(True)
