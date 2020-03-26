#!/bin/sh
#
# NTP_Client_RaspberryPiZero.sh - Configure NTP client on Raspberry Pi Zero
#
# 17 March 2020 - 1.0
#
# Author: Ruben Condesso - 81969 - 2nd Semester (2020)
#
#
# SmartBike System - Master Thesis in Telecommunications and Computer Engineering
#
#
# Script that configures NTP client on Raspberry Pi Zero
#
#


clear

echo "================================================================="
echo "========== Setting up NTP Client on Raspberry Pi Zero ==========="
echo "================================================================="



####################################################################################### Install dependencies  ########################################################################################

#sudo apt-get -y install ntp


############################################################################### Back up existing configuration files #################################################################################

echo "Backing up existing config files"

if [ -f /etc/ntp.conf ]
then
	cp /etc/ntp.conf /etc/ntp.conf.backup
fi


#################################################################################### NTP Client Configuration ########################################################################################


sudo systemctl stop systemd-timesyncd
sudo systemctl disable systemd-timesyncd
​sudo /etc/init.d/ntp stop
​sudo /etc/init.d/ntp start

# Configure /etc/ntp.conf
sudo bash -c 'cat > /etc/ntp.conf' << EOF
#/etc/ntp.conf, configuration for ntpd

driftfile /var/lib/ntp/ntp.drift
statsdir /var/log/ntpstats/

statistics loopstats peerstats clockstats
filegen loopstats file loopstats type day enable
filegen peerstats file peerstats type day enable
filegen clockstats file clockstats type day enable

# You do need to talk to an NTP server or two (or three).
server 192.168.0.2

# pool.ntp.org maps to more than 300 low-stratum NTP servers.
# Your server will pick a different set every time it starts up.
# *** Please consider joining the pool! ***
# *** ***


# By default, exchange time with everybody, but don't allow configuration.
# See /usr/share/doc/ntp-doc/html/accopt.html for details.
restrict -4 default kod notrap nomodify nopeer noquery
restrict -6 default kod notrap nomodify nopeer noquery

# Local users may interrogate the ntp server more closely.
restrict 127.0.0.1
restrict ::1

# Clients from this (example!) subnet have unlimited access,
# but only if cryptographically authenticated
#restrict 192.168.123.0 mask 255.255.255.0 notrust

# If you want to provide time to your local subnet, change the next line.
# (Again, the address is an example only.)
#broadcast 192.168.123.255

# If you want to listen to time broadcasts on your local subnet,
# de-comment the next lines. Please do this only if you trust everybody
# on the network!
#disable auth
#broadcastclient
EOF

# Restart ntp service
sudo service ntp reload

# Check ntp service running
sudo ntpq -p
