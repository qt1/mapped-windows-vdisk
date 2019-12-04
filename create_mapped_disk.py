#!/usr/bin/python3

# create loop devices and dmsetup
# abort on error so the diske will not be created if anythong goes wrong

import subprocess

start_part_file = 'mbr_and_3partitions.raw'
end_part_file = 'gpt2.raw'
target_device_name='virtual_windows_disk'

loop1 = subprocess.check_output(['losetup','--find','--show', start_part_file]).decode('utf-8')
loop2 = subprocess.check_output(['losetup','--find','--show', end_part_file]).decode('utf-8')
loop1_template='/dev/loop15'
loop2_template='/dev/loop16'
def_file_template_name='virtual_windows_disk_def'
def_file_name=def_file_template_name+'_current'

# verify we got good loop names

if(not loop1.startswith('/dev/loop')):
    print("Error creating loop1. "+loop1)
    exit(1)
print(f'loop1 = {loop1}')

if(not loop2.startswith('/dev/loop')):
    subprocess.check_output(['losetup','--delete', loop1])
    print("Error creating loop2. "+loop1)
    exit(1)
print(f'loop2 = {loop2}')

with open(def_file_template_name,'r') as tf:
    template = tf.read()


loop1=loop1.replace('\n','')
loop2=loop2.replace('\n','')
template = template.replace(loop1_template,loop1)
templete = template.replace(loop2_template,loop2)
print(f'template = {template}')

with open(def_file_name,'w') as of:
    of.write(template)

rc = subprocess.check_output(['dmsetup', 'create', target_device_name, def_file_name])
print(rc)
