# nwpa
Wifi setup and connection without systemd or NetworkManager

As an Arch Linux user, I used to use their netctl for wifi setup and connection. But that was deprecated, and I was 'forced' to use systemd-networkd or NetworkManager or whatever. I wanted something that was simpler and didn't require daemons (except for dhcpcd).

So I created this Python script that uses wpa_supplicant and dhcpcd. The program should work on any Linux system that has Python 3.xx. It uses both text-based and gui. It first determines what the wifi device is, then scans for wifi networks, and compares those networks to networks you've connected to in the past. If one is available, it connects to it using wpa_supplicant. If not, it invites you to create a new wpa_supplicant conf file and connects to that. 

The naming convention for a wpa_supplicant conf file is that it will reside in the /etc/wpa_supplicant directory and be named wpa_supplicant.[SSID].conf.

Arch Linux is that only distribution I've tried it on.

