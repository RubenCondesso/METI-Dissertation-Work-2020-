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


echo "Configuration Files are backed up."

