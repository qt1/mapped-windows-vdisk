#!/usr/bin/python3

# create loop devices and dmsetup
# abort on error so the diske will not be created if anythong goes wrong

import subprocess

start_part_file = 'mbr_and_3partitions.raw'
end_part_file = 'gpt2.raw'
target_device_name = 'virtual_windows_disk'
loop1_template = 'dev_loop1_template'
loop2_template = 'dev_loop2_template'
def_file_template_name = 'virtual_windows_disk_def'
def_file_name = def_file_template_name+'_current'

# TBD: Verify the disk structure is not changed - the disk and partitions IDs and sizes 
#      of the config match the physical disk 

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

rc = subprocess.check_output(['dmsetup', 'create', target_device_name, def_file_name])
print(rc)
