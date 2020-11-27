import os
import shutil
from pathlib import Path


def get_obj_name(files):
    for file in files:
        if (str(file).endswith(".obj")):
            return (str(file).split('.')[0], True)
    return (None, False)

def filter_specify_file(root, files, name, type, verbose=False):
    output = []
    for file in files:
        if (file.startswith(name) and os.path.splitext(file)[-1] in type):
            output.append(os.path.join(root, file))

    if verbose :
        if (len(output) != 2) :
            print("Filter ERROR\n")
            while(1):
                pass
        print(output)
    return output

def inverse_find(base, verbose=False):
    output = []
    for root, dirs, files in os.walk(base):
        name, ans = get_obj_name(files)
        if (ans is True):
            tmp = filter_specify_file(root, files, name, ['.obj', '.bmp'])
            if (len(tmp) > 0):
                output.append(tmp)
    return output

def copy(output, target_dir, verbose=False):
    for file_pair in output:
        for file in file_pair:
            source = file
            target_file = os.path.join(target_dir, source.split('/')[-1])
            if verbose:
                print("Source = ", file)
                print("target = ", target_file)
            if Path(target_file).exists():
                print("Skipped : {0}".format(source))
            else:
                shutil.copy(source, target_dir)
                if (Path(target_file).exists()):
                    print("Copyed successfully : {0} ".format(source))
                else:
                    print("Error")
                    while(1):
                        pass

if __name__ == '__main__':
    base_path = "/home/li_gang/TestFile/dataBase"
    target_dir = '/home/li_gang/TestFile/LargeInput1'
    out = inverse_find(base_path)
    copy(out, target_dir)