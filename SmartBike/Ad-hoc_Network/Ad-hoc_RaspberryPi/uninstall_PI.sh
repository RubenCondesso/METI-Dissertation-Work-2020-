#!/bin/bash

# Turn off the Ad-Hoc network and restore the previous wlan configuration


#############################	Error handling	##############

#DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )" # Directory where this script is

PROGNAME=$(basename $0) # A slicker error handling routine by William Shotts (www.linuxcommand.org)
error_exit() {
	echo "${PROGNAME}: ${1:-"Unknown Error"}" 1>&2
	exit 1
}

	

#############################	Start of script	##############################


#Restore interface config and removing backup
sudo cp /etc/network/interfaces.backup /etc/network/interfaces || error_exit "$LINENO: I couldn't restore the backup."
sudo rm /etc/network/interfaces.backup || error_exit "$LINENO: I couldn't delete the backup."
sudo iwconfig wlan0 mode Managed

sudo ifconfig wlan0 down #Turn off the wireless interface of Raspberry Pi
sudo ifconfig wlan0 up # Tunr on the wireless interface  of Raspberry Pi

sudo iwlist wlan0 scan # Scan the networks available
sudo iwconfig # Show actual interfaces settings

echo "All settings restored" && exit 0