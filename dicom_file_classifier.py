import os
import os.path
import pydicom
import shutil
from multiprocessing import Process
import time

# set initial values
src_path = "dicom file directory"
des_path = "destination directory"
process_count = 10    # number of process you use

def sd_form(str):    # Series Description
    str = str.replace(' ', '_')
    str = str.replace('<', '_')
    str = str.replace('>', '_')
    str = str.upper()
    return str

def sn_form(str):    # Series Number
    str = str.zfill(4)
    return str

def pn_form(str):    # Patient Number
    str = str.replace(' ', '_')
    str = str.upper()
    return str

def create_folder(dir):    # create new folder # only if folder doesn't exists
    if os.path.isdir(dir):
        return
    try:
        os.makedirs(dir)    
        print(f"Folder created \"{dir}\"")
    except FileExistsError:
        print(f"[Error] while creating new folder \"{dir}\"")

def get_dirs(path):
    dir_list = list()
    dirs = os.listdir(path)
    for dir in dirs:
        dir_path = os.path.join(path, dir)
        if os.path.isdir(dir_path):
            dir_list.append(dir_path)
    return dir_list

def split_num(num, divisor):    # set number of folders allocated to a process
    l = list()
    range_list = list()
    q, r = divmod(num, divisor)
    for i in range(divisor):
        l.append(q)
    for i in range(r):
        l[i] += 1
    for i, n in enumerate(l):
        n += sum(l[:i])
        range_list.append(n)
    return range_list

def split_list(dir_list, num_pr):
    total = list()
    num_dir = len(dir_list)
    range_list = split_num(num_dir, num_pr)
    index = 0
    for n in range_list:
        total.append(dir_list[index:n])
        index = n
    return total

def create_dcm_folder(id, new_path, path_list):
    for path in path_list:
        for root, dirs, files in os.walk(path):
            rootpath = os.path.join(path, root)
            for file in files:
                filepath =os.path.join(rootpath, file)
                # headers info for foldername
                header = pydicom.dcmread(filepath, specific_tags=['SeriesDescription', 'SeriesNumber', 'PatientName', 'PatientID'])
                series_des_raw = str(header[header.data_element('SeriesDescription').tag].value)
                series_des = sd_form(series_des_raw)
                series_num_raw = str(header[header.data_element('SeriesNumber').tag].value)
                series_num = sn_form(series_num_raw)
                patient_name_raw = str(header[header.data_element('PatientName').tag].value)
                patient_name = pn_form(patient_name_raw)
                patient_id = str(header[header.data_element('PatientID').tag].value)

                parentF_name = f'{patient_name}_{patient_id}'
                subF_name = f'{series_des}_{series_num}'
                new_folder_path = os.path.join(new_path, parentF_name, subF_name)
                create_folder(new_folder_path)
                shutil.copy2(filepath, new_folder_path)    # copy file # (filepath) > (new_folder_path)

##################################################
if __name__ == "__main__":
    start = time.time()
    path = os.path.abspath(src_path)
    new_path = os.path.abspath(des_path)
    dir_list = get_dirs(path)
    dir_list = split_list(dir_list, process_count)
    print(dir_list)
    process_l = list()
    for i, dir in enumerate(dir_list):
        p = Process(target=create_dcm_folder, args=(i, new_path, dir))
        p.start()
        process_l.append(p)
    for p in process_l:
        p.join()
    print(f"time: {time.time() - start}")
