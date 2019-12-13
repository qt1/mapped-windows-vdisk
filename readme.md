# Disk dual boot+VM

The windows.solid isk is intended tobe used from both VM (normal use) and Dual boot (full graphics)

It is possible to pass the root drive directly to the VM, and it actually works, However there is a danger of boothing to the host ' accessing the host disk at the same time from Vm and direct and corrupting everything.

The solution is to create a protected access path to the VM where the host partitions are invisible so the host root system is protected.


The apping consists of two parts:
1. A copy - where some parts of the main disk are kept + 2048 sectors for backup GPT
2. A link - a seperate reference to the Windows system disk (shared between Vm and dual boot)
3. empty filler
4. Ending GPT

The first part of the system disk containing MBR, recovery, EFI, and reserved is copied.

This looks safer at the moment ut it is possible that Windows uses this data for authentication and get engry at som point.

At the moment this risk seems reasonable..


# Instruction for creating the disk

list the source disk

    fdisk -l /dev/nvme0n1

results:

    Device             Start        End    Sectors   Size Type
    /dev/nvme0n1p1      2048    1085439    1083392   529M Windows recovery environme
    /dev/nvme0n1p2   1085440    1288191     202752    99M EFI System
    /dev/nvme0n1p3   1288192    1320959      32768    16M Microsoft reserved
    /dev/nvme0n1p4   1320960  408870911  407549952 194.3G Microsoft basic data
    /dev/nvme0n1p5 408872960  466874367   58001408  27.7G Linux filesystem
    /dev/nvme0n1p6 881569792 1953523711 1071953920 511.2G Linux filesystem

Copy the mbr and 3 partitions including EFI

    dd if=/dev/nvme0n1 of=mbr_and_3partitions.raw count=1320960   

Count is taken from the beginning of the start of the next partition + 2048 ending GPT


Create a loop device. Unfortuntly the loop numbers are taken by snap

so list the loop devices and find an empty slot

    ll /dev/loop*

And loop to the prefix and GPT2:

    losetup /dev/loop15 mbr_and_3partitions.raw
    losetup /dev/loop16 gpt2.raw

create the mapped file

    dmsetup create virtual_windows_disk virtual_windows_disk_def

First time only - fdisk and make sure the partitions are of the correct size

copy disk structure from source

    sfdisk -d /dev/nvme0n1 > nvme0n1.partition.table.txt


    sfdisk /dev/mapper/virtual_windows_disk < nvme0n1.partition.table.txt


After DM disk is ready it is possible to get the partitions rom the host like so:
(not needed for use as a VM disk)

    partprobe  /dev/mapper/virtual_windows_disk

# Running the mapping

The python script creates loop devices and runs the mapping. It should be called at system start or before running the VM.

    sudo python3 create_mapped_disk.py


# Systemd installation

The script and and various files are all located at /vm/windows10-solid

    sudo cp mapped_windows_disk.service /etc/systemd/system
    sudo chown root:adm /etc/systemd/system/mapped_windows_disk.service
    sudo chmod 664 /etc/systemd/system/mapped_windows_disk.service
    sudo systemctl enable mapped_windows_disk

run
    sudo systemctl run mapped_windows_disk

stop
    stop systemctl stop mapped_windows_disk

Note: at the moment the stop does not remove the loop devices


The following is usefull for debugging systemd service:
    sudo cp mapped_windows_disk.service /etc/systemd/system && sudo systemctl daemon-reload && sudo systemctl start mapped_windows_disk && journalctl -u mapped_windows_disk


# Reference

https://superuser.com/questions/931645/with-linux-mint-as-main-os-dual-boot-windows-7-and-have-a-windows-7-virtual-mac

http://www.linuxvoice.com/issues/005/pyparted.pdf

After DM disk is ready it is possible to get the partitions from the host like so:
This is for testng only and MUST NOT be done when running the windows VM

    partprobe /dev/sdX
