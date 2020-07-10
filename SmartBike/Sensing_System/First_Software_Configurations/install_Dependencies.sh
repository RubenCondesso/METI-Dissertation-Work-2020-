#!/bin/sh
#
# install_Dependencies.sh - Script for the Raspberry Pi Zero
#
# 16 April 2020 - 1.0
#
# Author: Ruben Condesso - 81969 - 2nd Semester (2020)
#
#
# SmartBike System - Master Thesis in Telecommunications and Computer Engineering
#
#
# Script that install all dependencies required for the SmartBike System in Raspberry Pi Zero
#
#

clear

echo "============================================================================="
echo "========== Installing all dependencies in the Raspberry Pi Zero  ============"
echo "============================================================================="


####################################################################################### Install dependencies  ########################################################################################

sudo apt -y update
sudo apt -y upgrade

# Install dnsmasq, dhcpcd and hostapd
sudo apt -y install dnsmasq dhcpcd hostapd

# Install NTP
sudo apt-get -y install ntp

# Update the package list
sudo apt-get update

# Install the dependencies
sudo apt-get install libdbus-1-dev libglib2.0-dev libudev-dev libical-dev libreadline-dev -y

# Install pip
sudo apt install python-pip

# Install dbus
sudo apt-get install python-dbus

# Install Numpy
sudo apt install python-numpy

# ---------------------------------------------------------------------------------------- Install BlueZ --------------------------------------------------------------------------------------------- #

#Download BlueZ source code
wget www.kernel.org/pub/linux/bluetooth/bluez-5.50.tar.xz

#Uncompress the downloaded file
tar xvf bluez-5.50.tar.xz && cd bluez-5.50

# Configure
./configure --prefix=/usr --mandir=/usr/share/man --sysconfdir=/etc --localstatedir=/var --enable-experimental

# Compile the source code
make -j4

# Install
sudo make install

# Reboot Raspberry Pi Zero
sudo reboot
