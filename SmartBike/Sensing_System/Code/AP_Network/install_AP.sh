#!/bin/sh
#
# install_AP.sh - Script for the Raspberry Pi Zero
#
# 04 March 2020 - 1.0
#
# Author: Ruben Condesso - 81969 - 2nd Semester (2020)
#
#
# SmartBike System - Master Thesis in Telecommunications and Computer Engineering
#
#
# Script that install and configure an access point in Raspberry Pi Zero
#
#

clear

echo "================================================================="
echo "========== Setting up Raspberry Pi Zero Access Point ============"
echo "================================================================="



####################################################################################### Install dependencies  ########################################################################################

#sudo apt -y update
#sudo apt -y upgrade
#sudo apt -y install dnsmasq dhcpcd hostapd


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

if [ -f /etc/dhcpcd.conf ]
then
	cp /etc/dhcpcd.conf /etc/dhcpcd.conf.backup
fi

if [ -f /etc/dnsmasq.conf ]
then
	cp /etc/dnsmasq.conf /etc/dnsmasq.conf.backup
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
  RUN+="/sbin/iw phy phy0 interface add wlan0 type __ap", \
  RUN+="/bin/ip link set wlan0 address ${MAC_ADDRESS}
EOF

# Configure /etc/dhcpcd.conf
sudo bash -c 'cat > /etc/dhcpcd.conf' << EOF
interface wlan0
    static ip_address=192.168.0.1/24
EOF

# Configure /etc/dnsmasq.conf
sudo bash -c 'cat > /etc/dnsmasq.conf' << EOF
interface=wlan0
  dhcp-range=192.168.0.2,192.168.0.20,255.255.255.0,24h
EOF

# Configure /etc/hostapd/hostapd.conf
sudo bash -c 'cat > /etc/hostapd/hostapd.conf' << EOF
interface=wlan0
driver=nl80211
ssid=SmartBike_AP
hw_mode=g
channel=7
wmm_enabled=0
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
wpa=2
wpa_passphrase=1234567890
wpa_key_mgmt=WPA-PSK
wpa_pairwise=TKIP
rsn_pairwise=CCMP
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

# Configure /bin/launch_AP.sh
sudo bash -c 'cat > /bin/launch_AP.sh' << EOF
echo 'Starting Access Point on Raspberry Pi Zero'
sleep 50
sudo ifdown --force wlan0
sudo ifup wlan0
sudo sysctl -w net.ipv4.ip_forward=1
sudo iptables -t nat -A POSTROUTING -s 192.168.0.0/24 ! -d 192.168.0.0/24 -j MASQUERADE
sudo systemctl restart dnsmasq
EOF

# Set permissions to run this script
sudo chmod +x /bin/launch_AP.sh
crontab -l | { cat; echo "@reboot /bin/launch_AP.sh"; } | crontab -
echo "Access Point configuration is finished! Please reboot your Raspberry Pi Zero to apply the changes made."
