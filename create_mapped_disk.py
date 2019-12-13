#!/usr/bin/python3

# create loop devices and dmsetup
# abort on error so the diske will not be created if anythong goes wrong

import subprocess
import sys
import os

script_path = os.path.dirname(os.path.abspath(__file__))

start_part_file = 'mbr_and_3partitions.raw'
end_part_file = 'gpt2.raw'
target_device_name = 'virtual_windows_disk'
loop1_template = 'dev_loop1_template'
loop2_template = 'dev_loop2_template'
def_file_template_name = 'virtual_windows_disk_def'
def_file_name = def_file_template_name+'_current'

# TBD: Verify the disk structure is not changed - the disk and partitions IDs and sizes
#      of the config match the physical disk


def create_mapped_disk():
    loop1 = subprocess.check_output(['losetup', '--find', '--show', start_part_file]).decode('utf-8')
    loop2 = subprocess.check_output(['losetup', '--find', '--show', end_part_file]).decode('utf-8')
    loop1 = loop1.replace('\n', '')
    loop2 = loop2.replace('\n', '')

    # verify we got good loop names

    if(not loop1.startswith('/dev/loop')):
        print("Error creating loop1. "+loop1)
        exit(1)
    print(f'loop1 = {loop1}')

    if(not loop2.startswith('/dev/loop')):
        subprocess.check_output(['losetup', '--delete', loop1])
        print("Error creating loop2. "+loop2)
        exit(1)
    print(f'loop2 = {loop2}')

    with open(def_file_template_name, 'r') as tf:
        template = tf.read()

    # replace the actual loop names into the config template and create the device
    t1 = template.replace(loop1_template, loop1)
    t2 = t1.replace(loop2_template, loop2)
    print(f'template = {t2}')

    # For some reson the following did hot do the second substitution
    #
    # template = template.replace(loop1_template, loop1)
    # template = template.replace(loop2_template, loop2)

    with open(def_file_name, 'w') as of:
        of.write(t2)

    try:
        output = subprocess.check_output(['dmsetup', 'create', target_device_name, def_file_name], stderr=subprocess.STDOUT)
        # output = subprocess.check_output(
        # cmnd, stderr=subprocess.STDOUT, shell=True, timeout=3,
        # universal_newlines=True)
    except subprocess.CalledProcessError as exc:
        print(f"Status : FAIL - RC={exc.returncode}, output={exc.output}")
    else:
        print(f"Output: \n{output}\n")


def remove_mapped_disk():
    print(f"removing device {target_device_name}")
    rc = subprocess.check_output(['dmsetup', 'remove', target_device_name])
    print(rc)
    # TBD: also remove loop devices


if __name__ == "__main__":

    work_path = sys.argv[2] if len(sys.argv) == 3 else script_path

    os.chdir(work_path)

    if len(sys.argv)>1 and sys.argv[1] == 'start':
        create_mapped_disk()
    elif len(sys.argv)>1 and sys.argv[1] == 'stop':
        remove_mapped_disk()
    else:
        print(f'{sys.argv[0]} Error: expecting either "start" or "stop"')
        sys.exit(2)
