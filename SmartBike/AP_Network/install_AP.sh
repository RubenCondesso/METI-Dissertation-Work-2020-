#!/bin/sh
#
# install_AP.sh - Script for the Raspberry Pi Zero
#
# 01 March 2020 - 1.0 
# 
# Autor: Ruben Condesso - 81969 - 2nd Semester (2020)
#
# 
# SmartBike System - Master Thesis in Telecomunications and Computer Engineering
#
# 
# Script that install and configure an access point in Raspberry Pi Zero
# 
#

clear

echo "======================================================="
echo "===== Setting up Raspberry Pi Zero Access Point ======="
echo "======================================================="



####################################################################################### Install dependencies  ########################################################################################

sudo apt -y update
sudo apt -y upgrade
sudo apt -y install dnsmasq dhcpcd hostapd


############################################################################### Back up existing configuration files #################################################################################

echo "Backing up existing config files"

if [ -f /etc/udhcpd.conf ]
then
	cp /etc/udhcpd.conf /etc/udhcpd.conf.backup
fi

if [ -f /etc/default/udhcpd ]
then
	cp /etc/default/udhcpd /etc/default/udhcpd.backup
fi

if [ -f /etc/network/interfaces ]
then
	cp /etc/network/interfaces /etc/network/interfaces.backup
fi

if [ -f /etc/hostapd/hostapd.conf ]
then
	cp /etc/hostapd/hostapd.conf /etc/hostapd/hostapd.conf.backup
fi

if [ -f /etc/default/hostapd ]
then
	cp /etc/default/hostapd /etc/default/hostapd.backup
fi

if [ -f /etc/sysctl.conf ]
then
	cp /etc/sysctl.conf /etc/sysctl.conf.backup
fi


if [ -f /etc/iptables.ipv4.nat ]
then
	cp /etc/iptables.ipv4.nat /etc/iptables.ipv4.nat.backup
fi

if [ -f /etc/wpa_supplicant/wpa_supplicant.conf ]
then
	cp /etc/wpa_supplicant/wpa_supplicant.conf /etc/wpa_supplicant/wpa_supplicant.conf.backup
fi


echo "Configuration files are backed up."


################################################################################# Access Point Configuration ####################################################################################


# Configure /etc/udev/rules.d/70-persistent-net.rules
sudo bash -c 'cat > /etc/udev/rules.d/70-persistent-net.rules' << EOF
SUBSYSTEM=="ieee80211", ACTION=="add|change", ATTR{macaddress}=="${MAC_ADDRESS}", KERNEL=="phy0", \
  RUN+="/sbin/iw phy phy0 interface add ap0 type __ap", \
  RUN+="/bin/ip link set ap0 address ${MAC_ADDRESS}
EOF


# Configure /etc/dnsmasq.conf
sudo bash -c 'cat > /etc/dnsmasq.conf' << EOF
interface=wlan0
dhcp-range=192.168.0.50,192.168.0.150,255.255.255.0,12h
dhcp-option=3,192.168.0.1
listen-address=127.0.0.1
EOF

# Configure /etc/hostapd/hostapd.conf
sudo bash -c 'cat > /etc/hostapd/hostapd.conf' << EOF
interface=wlan0
hw_mode=g
channel=6
ieee80211n=1
wmm_enabled=1
ssid=SmartBike_AP
auth_algs=1
wpa=2
wpa_key_mgmt=WPA-PSK
rsn_pairwise=CCMP
wpa_passphrase=123456789
EOF

# Configure /etc/wpa_supplicant/wpa_supplicant.conf
sudo bash -c 'cat > /etc/wpa_supplicant/wpa_supplicant.conf' << EOF
country=PT
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1
EOF

# Configure /etc/default/hostapd
sudo bash -c 'cat > /etc/default/hostapd' << EOF
DAEMON_CONF="/etc/hostapd/hostapd.conf"
EOF

# Configure /etc/network/interfaces
sudo bash -c 'cat > /etc/network/interfaces' << EOF
source-directory /etc/network/interfaces.d
auto lo
iface lo inet loopback

auto wlan0
iface wlan0 inet static
    address 192.168.10.1
    netmask 255.255.255.0
    hostapd /etc/hostapd/hostapd.conf
EOF

# Configure /bin/launch_AP.sh
sudo bash -c 'cat > /bin/launch_AP.sh' << EOF
echo 'Starting Access Point.'
sleep 30
sudo ifdown --force wlan0
sudo ifup wlan0
sudo sysctl -w net.ipv4.ip_forward=1
sudo iptables -t nat -A POSTROUTING -s 192.168.10.0/24 ! -d 192.168.10.0/24 -j MASQUERADE
sudo systemctl restart dnsmasq
EOF

# Set permissions to run this script
sudo chmod +x /bin/launch_AP.sh
crontab -l | { cat; echo "@reboot /bin/launch_AP.sh"; } | crontab -
echo "Access Point configuration is finished! Please reboot your Raspberry Pi Zero to apply the changes made."
