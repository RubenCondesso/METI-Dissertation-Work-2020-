#!/bin/bash
#
# install_BlueZ.sh
#
# 29 Fev 2020 - 1.0 
# 
# Autor: Ruben Condesso - 81969 - 2nd Semester (2020)
#
# 
# SmartBike System - Master Thesis in Telecomunications and Computer Engineering
#
# 
# Script that installs BlueZ on Raspberry Pi Zero
# 
#

# -------------------------------------------------------------------------------------- Install Dependencies ----------------------------------------------------------------------------------------- #

# Update the package list
sudo apt-get update

# Install the dependencies
sudo apt-get install libdbus-1-dev libglib2.0-dev libudev-dev libical-dev libreadline-dev -y

# Install pip 
sudo apt install python-pip

# Install dbus
sudo apt-get install python-dbus


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