#!/usr/bin/env python3

import socket, sys, shlex
import easygui_qt as easy
import subprocess as sp
import inquirer as inq

#global variables
known_ssids = []
wpa_dir = '/etc/wpa_supplicant/'
wpa = 'wpa_supplicant'
trigger = 0

def g(words):
	comlist = []
	for line in shlex.split(words):
            comlist.append(line)
	return comlist

def dirls(directory):
    if len(directory) == 0:
        command = g('ls')
        listing = sp.check_output(command,stderr=sp.PIPE).decode().split('\n')
    else:
        command = g('ls')
        listing = sp.check_output(command,cwd = directory,stderr=sp.PIPE).decode().split('\n')
    listing.pop(-1)
    return listing

def get_known_ssids():
    first_list = dirls(wpa_dir)
    for line in first_list:
        known_ssids.append(line.split('.')[1])
    return known_ssids

def get_device_name():
    dev_list = []
    command = g('sudo iw dev')
    raw = sp.run(command, text = True, stdout = sp.PIPE)
    result = raw.stdout.split('\n')
    for line in result:
        if 'Interface' in line:
            device_name = line.split(' ')[1]
    return device_name

def setup_device():
    command = g(f'sudo ip link set {device_name} up')
    sp.run(command)
    return

def scan_for_ssids():
    scan_list = []
    command = g(f'sudo iw dev {device_name} scan')
    raw = sp.run(command, text = True, stdout = sp.PIPE)
    result = raw.stdout.split('\n')
    for line in result:
        if 'SSID:' in line and line.split(' ')[1] not in scan_list:
            scan_list.append(line.split(' ')[1])
    return scan_list

def check_for_matched_ssids():
    matched = 'no_matches'
    for line in known_ssids:
        for item in scan_list:
            if line == item:
                matched = item
    return matched

def create_new_wpa():
    three_lines = "ctrl_interface=DIR=/var/run/wpa_supplicant\nupdate_config=1\nnetwork={\n\tssid="
    pick_ssid = inq.list_input('Select SSID name',choices = scan_list)
    three_lines = three_lines+'"'+pick_ssid+'"\n'
    password = inq.text('Enter password')
    if password == '':
        three_lines = three_lines+'\tkey_mgmt=NONE\n}'
    else:
        three_lines = three_lines+'\tpsk="%s"\n}'%(password)
    return three_lines,pick_ssid

def get_ssid_conf_file():
    if matched_ssid == 'no_matches':
        print('\nThere were no matches for available SSIDS in your wpa_supplicant folder.\n')
        yesno = inq.confirm('Do you want to create a new wpa.conf file',default = True)
        if not yesno:
            sys.exit()
        new_wpa,pick_ssid = create_new_wpa()
        with open('temp_ssid.txt','w') as f:
            f.writelines(new_wpa)
        command = g('sudo cp temp_ssid.txt %s%s.%s.conf'%(wpa_dir,wpa,pick_ssid))
        sp.run(command)
        command = g('rm temp_ssid.txt')
        sp.run(command)
        ssid_conf_file = wpa_dir+wpa+'.'+pick_ssid+'.conf'
    else:
        ssid_conf_file = wpa_dir+wpa+'.'+matched_ssid+'.conf'
    return ssid_conf_file

def start_wpa_supplicant():
    trigger = 0
    command = g('sudo killall -9 wpa_supplicant')
    sp.run(command, text = True, stdout = sp.PIPE, stderr = sp.PIPE)
    command = g(f'sudo wpa_supplicant -B -D nl80211 -i {device_name} -c {ssid_conf_file}')
    raw = sp.run(command,text = True, stdout = sp.PIPE, stderr = sp.PIPE)
    if len(raw.stdout) > 0 and matched_ssid != 'no_matches':
        print(f'Connected to {matched_ssid}')
    else:
        print(raw.stderr)
    return

def start_dhcpcd():
    command = g(f'sudo dhcpcd {device_name}')
#    command = g(f'sudo systemctl start dhcpcd@{device_name}')
    sp.run(command, text = True, stdout = sp.PIPE, stderr = sp.PIPE)

def check_internet():
    print('\nProgram will terminate when Internet connection is verified')

    command = g('dig +short myip.opendns.com @resolver1.opendns.com')

    ip_info = sp.run(command, text = True, stdout = sp.PIPE, stderr = sp.PIPE)

    if len(ip_info.stderr) == 0:
        internet_address = ip_info.stdout.rstrip('\n')
        yesno = 0

    else:
        print('Failed to connect to the Internet')
        yesno = inq.confirm('Try connection again (no will terminate program)',default = True)

    return yesno

def get_lan_ip():
    ipaddress = '0.0.0.0'
    while ipaddress == '0.0.0.0':
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(('10.1.2.2',1))
            ipaddress = s.getsockname()[0]
        except OSError:
            ipaddress = '0.0.0.0'
    s.close()
    return ipaddress





print('\nMatching existing SSIDs to those available on WiFi\n')
known_ssids = get_known_ssids()
device_name = get_device_name()
setup_device()
scan_list = scan_for_ssids()
matched_ssid = check_for_matched_ssids()
ssid_conf_file = get_ssid_conf_file()
start_wpa_supplicant()
start_dhcpcd()
lan_address = get_lan_ip()
print(f'\n{lan_address} assigned to {device_name}. Checking Internet connection\n')
check_internet()

easy.show_message(f'Device {device_name} with IP {lan_address} is connected to the Internet')








    
